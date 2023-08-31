""" Automatically generated from the DTD of Jmdict Rev 1.09 using xsdata """

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ExSent:
    class Meta:
        name = "ex_sent"

    lang: str = field(
        default="eng",
        metadata={
            "type": "Attribute",
            "namespace": "http://www.w3.org/XML/1998/namespace",
            "required": True,
        }
    )
    value: str = field(
        default="",
        metadata={
            "required": True,
        }
    )


@dataclass
class ExSrce:
    class Meta:
        name = "ex_srce"

    exsrc_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    value: str = field(
        default="",
        metadata={
            "required": True,
        }
    )


@dataclass
class Gloss:
    class Meta:
        name = "gloss"

    lang: str = field(
        default="eng",
        metadata={
            "type": "Attribute",
            "namespace": "http://www.w3.org/XML/1998/namespace",
            "required": True,
        }
    )
    g_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    g_gend: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    content: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
            "choices": (
                {
                    "name": "pri",
                    "type": str,
                },
            ),
        }
    )


@dataclass
class KEle:
    class Meta:
        name = "k_ele"

    keb: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    ke_inf: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    ke_pri: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class Lsource:
    class Meta:
        name = "lsource"

    lang: str = field(
        default="eng",
        metadata={
            "type": "Attribute",
            "namespace": "http://www.w3.org/XML/1998/namespace",
            "required": True,
        }
    )
    ls_wasei: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    ls_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    value: str = field(
        default="",
        metadata={
            "required": True,
        }
    )


@dataclass
class REle:
    class Meta:
        name = "r_ele"

    reb: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    re_nokanji: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    re_restr: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    re_inf: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    re_pri: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class Example:
    class Meta:
        name = "example"

    ex_srce: Optional[ExSrce] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    ex_text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    ex_sent: List[ExSent] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        }
    )


@dataclass
class Sense:
    class Meta:
        name = "sense"

    stagk: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    stagr: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    pos: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    xref: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    ant: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    field_value: List[str] = field(
        default_factory=list,
        metadata={
            "name": "field",
            "type": "Element",
        }
    )
    misc: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    s_inf: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    lsource: List[Lsource] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    dial: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    gloss: List[Gloss] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    example: List[Example] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class Entry:
    class Meta:
        name = "entry"

    ent_seq: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    k_ele: List[KEle] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    r_ele: List[REle] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        }
    )
    sense: List[Sense] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        }
    )


@dataclass
class Jmdict:
    class Meta:
        name = "JMdict"

    entry: List[Entry] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
