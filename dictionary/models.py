import django.db.models as models

class Entry(models.Model):
  ent_seq = models.PositiveIntegerField(primary_key=True)

class Entity(models.Model):
  uid = models.IntegerField(primary_key=True)
  desc = models.CharField(max_length=64, unique=True)
  
class KEle(models.Model):
  uid = models.IntegerField(primary_key=True)
  entry = models.ForeignKey(Entry, on_delete=models.CASCADE)

  keb = models.CharField(max_length=64, null=False, blank=False)
  ke_inf = models.ManyToManyField(Entity, related_name='ke_inf')
  ke_pri = models.ManyToManyField(Entity, related_name='ke_pri')

class REle(models.Model):
  uid = models.IntegerField(primary_key=True)
  entry = models.ForeignKey(Entry, on_delete=models.CASCADE)

  reb = models.CharField(max_length=64)
  hepburn = models.CharField(max_length=192)
  re_nokanji = models.BooleanField()
  re_restr = models.ManyToManyField(KEle)
  re_inf = models.ManyToManyField(Entity, related_name='re_inf')
  re_pri = models.ManyToManyField(Entity, related_name='re_pri')

class Sense(models.Model):
  uid = models.IntegerField(primary_key=True)
  entry = models.ForeignKey(Entry, on_delete=models.CASCADE)

  stagk = models.ManyToManyField(KEle)
  stagr = models.ManyToManyField(REle)
  pos = models.ManyToManyField(Entity, related_name='pos')
  # xref = models.ManyToManyField(Entry)
  # ant = models.ManyToManyField(Entry)
  field = models.ManyToManyField(Entity, related_name='field')
  misc = models.ManyToManyField(Entity, related_name='misc')
  s_inf = models.CharField(max_length=64, null=True)
  dial = models.ManyToManyField(Entity, related_name='dial')

# class Example

class LSource(models.Model):
  sense = models.ForeignKey(Sense, on_delete=models.CASCADE)

  lang = models.CharField(max_length=8, default='eng')
  ls_wasei = models.BooleanField(default=False)
  ls_type = models.CharField(max_length=8, default='full', null=True)
  value = models.CharField(max_length=64, null=True)

class Gloss(models.Model):
  sense = models.ForeignKey(Sense, on_delete=models.CASCADE)

  lang = models.CharField(max_length=8, default='eng')
  g_type = models.CharField(max_length=8, null=True)
  g_gend = models.CharField(max_length=8, null=True)
  content = models.CharField(max_length=64, null=True)