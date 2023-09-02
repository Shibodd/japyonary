from argparse import ArgumentParser
from django.core.management.base import BaseCommand
from pathlib import Path
from xsdata.formats.dataclass.parsers import XmlParser
from typing import Callable

from . import jmdict_xml
import dictionary.models as models
import pickle
import itertools
import romkan

def load_jmd_xml(path: Path) -> jmdict_xml.Jmdict:
  if isinstance(path, str):
    path = Path(path)

  pickled_path = path.with_suffix(".pickle")
  if pickled_path.exists():
    print("Found pickled dictionary. Loading...")
    with pickled_path.open('rb') as f:
      return pickle.Unpickler(f).load()
      
  else:
    print("Parsing xml dictionary...")
    parser = XmlParser()
    jd = parser.from_path(path, jmdict_xml.Jmdict)

    print("Writing pickled dictionary...")
    with pickled_path.open('wb') as f:
      pickle.Pickler(f).dump(jd)
    return jd

  
def load_entities(jmd: jmdict_xml.Jmdict) -> set[str]:
  """ 
  Iterates the whole dictionary to return a set of distinct entities from a fixed set of fields. 
  TODO: load them directly from the DTD.
  """

  ans = set()
  for entry in jmd.entry:
    for k_ele in entry.k_ele:
      ans.update(k_ele.ke_inf)
      ans.update(k_ele.ke_pri)
    for r_ele in entry.r_ele:
      ans.update(r_ele.re_inf)
      ans.update(r_ele.re_pri)
    for sense in entry.sense:
      ans.update(sense.field_value)
      ans.update(sense.dial)
      ans.update(sense.misc)
      ans.update(sense.pos)

  return ans

def resolve_inter_entry_links(jmd: jmdict_xml.Jmdict):
  def single(xs: list):
    assert(len(xs) == 1)
    return xs[0]

  def resolve_k(entry: jmdict_xml.Entry, ks):
    return [
      single([k_ele for k_ele in entry.k_ele if k_ele.keb == k])
      for k in ks
    ]

  def resolve_r(entry: jmdict_xml.Entry, rs):
    return [
      single([r_ele for r_ele in entry.r_ele if r_ele.reb == r])
      for r in rs
    ]

  for entry in jmd.entry:
    for r_ele in entry.r_ele:
      r_ele.re_restr = resolve_k(entry, r_ele.re_restr)
    for sense in entry.sense:
      sense.stagk = resolve_k(entry, sense.stagk)
      sense.stagr = resolve_r(entry, sense.stagr)

def update_db(jmd: jmdict_xml.Jmdict):
  def create_lookup_on_object_id(xml_objs, db_objs):
    # The order is deterministic, so we can iterate twice over xml_objs to get a lookup table.
    return dict(zip(
      (id(xml_obj) for xml_obj in xml_objs),
      (db_obj.uid for db_obj in db_objs)
    ))
  
  print("Resolving links...")
  resolve_inter_entry_links(jmd)
  
  # Nuke the db
  print("Deleting objects...")
  models.Entity.objects.all().delete()
  models.Entry.objects.all().delete()

  # Entry
  print("Creating entries...")
  models.Entry.objects.bulk_create((models.Entry(ent_seq = entry.ent_seq) for entry in jmd.entry))

  # KEle
  print("Creating KEles...")
  k_ele_lookup = create_lookup_on_object_id(
    (k_ele for entry in jmd.entry for k_ele in entry.k_ele),
    models.KEle.objects.bulk_create(
      models.KEle(
        uid = i,
        entry_id = entry.ent_seq,
        keb = k_ele.keb
      )
      for (i, (entry, k_ele))
      in enumerate(
          (entry, k_ele)
          for entry in jmd.entry
          for k_ele in entry.k_ele)
    )
  )
  print(k_ele_lookup)

  # REle
  print("Creating REles...")
  r_ele_lookup = create_lookup_on_object_id(
    (r_ele for entry in jmd.entry for r_ele in entry.r_ele),
    models.REle.objects.bulk_create(
      models.REle(
        uid = i,
        entry_id = entry.ent_seq,
        reb = r_ele.reb,
        hepburn = romkan.to_hepburn(r_ele.reb),
        re_nokanji = r_ele.re_nokanji is not None
      )
      for (i, (entry, r_ele))
      in enumerate(
          (entry, r_ele)
          for entry in jmd.entry
          for r_ele in entry.r_ele)
    )
  )

  # Sense
  print("Creating Senses...")
  sense_lookup = create_lookup_on_object_id(
    (sense for entry in jmd.entry for sense in entry.sense),
    models.Sense.objects.bulk_create(
      models.Sense(
        uid = i,
        entry_id = entry.ent_seq,
        s_inf = sense.s_inf
      )
      for (i, (entry, sense))
      in enumerate(
          (entry, sense)
          for entry in jmd.entry
          for sense in entry.sense)
    )
  )

  # LSource
  print("Creating LSources...")
  models.LSource.objects.bulk_create(
    models.LSource(
      sense_id = sense_lookup[id(sense)],
      lang = lsource.lang,
      ls_wasei = lsource.ls_wasei is not None,
      ls_type = lsource.ls_type,
      value = lsource.value
    )
    for entry in jmd.entry
    for sense in entry.sense
    for lsource in sense.lsource
  )

  # Gloss
  print("Creating Glosses...")
  models.Gloss.objects.bulk_create(
    models.Gloss(
      sense_id = sense_lookup[id(sense)],
      lang = gloss.lang,
      g_type = gloss.g_type,
      g_gend = gloss.g_gend,
      content = gloss.content
    )
    for entry in jmd.entry
    for sense in entry.sense
    for gloss in sense.gloss
  )

  # Entity
  print("Creating entities...")
  # Create an entity lookup based on the entity description
  entity_lookup = dict(
    (entity.desc, entity.uid)
    for entity in models.Entity.objects.bulk_create(
      models.Entity(
        uid = i,
        desc = entity
      )
      for i, entity in enumerate(load_entities(jmd))
    )
  )

  # Create all many to many relationships
  models.KEle.ke_inf.through.objects.bulk_create(
    models.KEle.ke_inf.through(kele_id=k_ele_lookup[id(k_ele)], entity_id=entity_lookup[ke_inf])
    for entry in jmd.entry
    for k_ele in entry.k_ele
    for ke_inf in k_ele.ke_inf
  )
  models.KEle.ke_pri.through.objects.bulk_create(
    models.KEle.ke_pri.through(kele_id=k_ele_lookup[id(k_ele)], entity_id=entity_lookup[ke_pri])
    for entry in jmd.entry
    for k_ele in entry.k_ele
    for ke_pri in k_ele.ke_pri
  )
  models.REle.re_pri.through.objects.bulk_create(
    models.REle.re_pri.through(rele_id=r_ele_lookup[id(r_ele)], entity_id=entity_lookup[re_pri])
    for entry in jmd.entry
    for r_ele in entry.r_ele
    for re_pri in r_ele.re_pri
  )
  models.REle.re_inf.through.objects.bulk_create(
    models.REle.re_inf.through(rele_id=r_ele_lookup[id(r_ele)], entity_id=entity_lookup[re_inf])
    for entry in jmd.entry
    for r_ele in entry.r_ele
    for re_inf in r_ele.re_inf
  )
  models.Sense.stagk.through.objects.bulk_create(
    models.Sense.stagk.through(sense_id=sense_lookup[id(sense)], kele_id=k_ele_lookup[id(stagk)])
    for entry in jmd.entry
    for sense in entry.sense
    for stagk in sense.stagk
  )
  models.Sense.stagr.through.objects.bulk_create(
    models.Sense.stagr.through(sense_id=sense_lookup[id(sense)], rele_id=r_ele_lookup[id(stagr)])
    for entry in jmd.entry
    for sense in entry.sense
    for stagr in sense.stagr
  )
  models.Sense.pos.through.objects.bulk_create(
    models.Sense.pos.through(sense_id=sense_lookup[id(sense)], entity_id=entity_lookup[pos])
    for entry in jmd.entry
    for sense in entry.sense
    for pos in sense.pos
  )
  models.Sense.field.through.objects.bulk_create(
    models.Sense.field.through(sense_id=sense_lookup[id(sense)], entity_id=entity_lookup[field])
    for entry in jmd.entry
    for sense in entry.sense
    for field in sense.field_value
  )
  models.Sense.misc.through.objects.bulk_create(
    models.Sense.misc.through(sense_id=sense_lookup[id(sense)], entity_id=entity_lookup[misc])
    for entry in jmd.entry
    for sense in entry.sense
    for misc in sense.misc
  )
  models.Sense.dial.through.objects.bulk_create(
    models.Sense.dial.through(sense_id=sense_lookup[id(sense)], entity_id=entity_lookup[dial])
    for entry in jmd.entry
    for sense in entry.sense
    for dial in sense.dial
  )


class Command(BaseCommand):
  def add_arguments(self, parser: ArgumentParser):
    parser.add_argument('jmdict_path')

  def handle(self, *args, **options):
    jmd = load_jmd_xml(options['jmdict_path'])
    print("Dictionary loaded!")
    update_db(jmd)