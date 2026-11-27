"""Collateral check before a loan binds: are the late boxes real, the plant's, and free?

MOCK DATA, PROPOSED CHECK. Every order, document, lender and lot below is invented.
The check is what the brief and deck propose (pull request 8): before a loan
binds, confirm the late boxes' title is clear, that no bank or other lender
already holds them as security, and tie each lot to one swap so it cannot back
two. No real register, bank or document system is connected. The rules and the
tolerance are assumptions for a lender, broker and counsel to set.

Why: in a swap the late boxes are the lender's security. A reviewer from the
Lloyd's market will ask how we know that security is real and unpledged.

Four checks, all run every time, so a refusal lists every reason at once:

1. Document matches the order. The bill of lading or delivery order for the late
   boxes names the same booking, consignee, producer, producing plant, grade
   code, TEU and tonnes as the plant's order. Tonnes within `tonnes_tolerance`
   (default 0, exact; an assumption to set with the lender).
2. Plant holds the documents. Whoever holds the original document controls the
   goods, so the plant can only offer boxes whose document it holds. If a bank
   holds the originals (as under a letter of credit), the loan does not bind.
3. No other lender holds it as security. Any security interest on the document
   that is still in force on the bind day refuses the loan. One released on or
   before the bind day does not.
4. One lot backs one swap. The register refuses a document already tied to
   another live swap, and a swap that already has a lot. A lot is freed when its
   swap is released (the late boxes repaid the loan).

Split shipments: an order may travel under several bills of lading or delivery
orders. `check_split` runs the same four checks over all of them together: each
document must name the order's booking, parties and goods; together they must
carry exactly the order's TEU and its tonnes (within the tolerance); every one
must be held by the plant and free of security; and the whole set is tied to one
swap at once, so no part of it can back another. Assumption: all documents must
name the same vessel, because boxes on different vessels may arrive, and so
repay the loan, on different days; that case is refused, not handled.

Limits: names are compared ignoring case and outer spaces only; real documents
need a stricter party identifier.

Run:  (cd poc && python3 -m steadpoc.collateral)
"""
from dataclasses import dataclass, field
from typing import Optional

BANNER = "MOCK DATA: invented orders, documents and lenders. A proposed check, not a live system."
DOC_KINDS = ("bill of lading", "delivery order")
BIND_DAY = -8          # days relative to T, as in the demo's schedule (from the brief)

CHECK_MATCH = "document matches the order"
CHECK_HOLDER = "plant holds the documents"
CHECK_FREE = "no other lender holds it as security"
CHECK_ONE = "lot backs one swap only"
CHECKS = (CHECK_MATCH, CHECK_HOLDER, CHECK_FREE, CHECK_ONE)


def _need_text(**values):
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be given")


def _need_quantity(teu, tonnes):
    if isinstance(teu, bool) or not isinstance(teu, int) or teu <= 0:
        raise ValueError("teu must be a whole number above zero")
    if not tonnes > 0:
        raise ValueError("tonnes must be above zero")


@dataclass(frozen=True)
class Order:
    """What the plant bought: the late shipment, as on its purchase order."""
    booking: str
    consignee: str
    producer: str
    plant: str
    grade: str
    teu: int
    tonnes: float

    def __post_init__(self):
        _need_text(booking=self.booking, consignee=self.consignee, producer=self.producer,
                   plant=self.plant, grade=self.grade)
        _need_quantity(self.teu, self.tonnes)


@dataclass(frozen=True)
class TransportDoc:
    """The bill of lading or delivery order for the late boxes."""
    doc_ref: str
    kind: str
    booking: str
    consignee: str
    holder: str             # who holds the original document today
    producer: str
    plant: str
    grade: str
    teu: int
    tonnes: float
    vessel: str = ""

    def __post_init__(self):
        _need_text(doc_ref=self.doc_ref, booking=self.booking, consignee=self.consignee,
                   holder=self.holder, producer=self.producer, plant=self.plant, grade=self.grade)
        if self.kind not in DOC_KINDS:
            raise ValueError(f"kind must be one of {DOC_KINDS}")
        _need_quantity(self.teu, self.tonnes)


@dataclass(frozen=True)
class SecurityInterest:
    """A pledge, lien or letter-of-credit claim someone holds over a document's goods."""
    doc_ref: str
    holder: str
    kind: str                           # for example "bank pledge", "letter of credit"
    released_on: Optional[int] = None   # day relative to T; None = still in force

    def __post_init__(self):
        _need_text(doc_ref=self.doc_ref, holder=self.holder, kind=self.kind)

    def in_force_on(self, day: int) -> bool:
        return self.released_on is None or self.released_on > day


@dataclass(frozen=True)
class Finding:
    check: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class CollateralResult:
    swap_id: str
    doc_ref: str                        # one document, or several joined with ", "
    findings: tuple[Finding, ...]
    doc_refs: tuple[str, ...] = ()      # every document checked

    @property
    def binds(self) -> bool:
        return all(f.passed for f in self.findings)

    @property
    def reasons(self) -> list[str]:
        """Every reason the loan does not bind, in check order. Empty if it binds."""
        return [f.detail for f in self.findings if not f.passed]


@dataclass
class LotRegister:
    """One lot (one transport document) backs at most one live swap."""
    _by_doc: dict[str, str] = field(default_factory=dict)

    def swap_for(self, doc_ref: str) -> Optional[str]:
        return self._by_doc.get(doc_ref)

    def doc_for(self, swap_id: str) -> Optional[str]:
        docs = self.docs_for(swap_id)
        return docs[0] if docs else None

    def docs_for(self, swap_id: str) -> tuple[str, ...]:
        """Every document tied to a swap, in the order they were tied."""
        return tuple(d for d, sid in self._by_doc.items() if sid == swap_id)

    def problem(self, doc_ref: str, swap_id: str) -> Optional[str]:
        """Why tying this lot to this swap would break the one-lot rule, or None."""
        tied_to = self.swap_for(doc_ref)
        if tied_to is not None and tied_to != swap_id:
            return f"{doc_ref} already backs swap {tied_to}"
        has = self.doc_for(swap_id)
        if has is not None and has != doc_ref:
            return f"swap {swap_id} already has lot {has}; one lot per swap"
        return None

    def problems(self, doc_refs, swap_id: str) -> list[str]:
        """Why tying this set of documents to this swap would break the one-lot rule.

        The set is the lot. Any document already backing another swap is refused,
        and so is a swap that already holds a different set."""
        doc_refs = tuple(doc_refs)
        out = []
        for doc_ref in doc_refs:
            tied_to = self.swap_for(doc_ref)
            if tied_to is not None and tied_to != swap_id:
                out.append(f"{doc_ref} already backs swap {tied_to}")
        has = self.docs_for(swap_id)
        if has and set(has) != set(doc_refs):
            out.append(f"swap {swap_id} already has lot {', '.join(has)}; one lot per swap")
        return out

    def tie_all(self, doc_refs, swap_id: str) -> None:
        """Tie every document of a split shipment to one swap, all or none."""
        doc_refs = tuple(doc_refs)
        _need_text(swap_id=swap_id)
        if not doc_refs:
            raise ValueError("at least one document must be given")
        for doc_ref in doc_refs:
            _need_text(doc_ref=doc_ref)
        if len(set(doc_refs)) != len(doc_refs):
            raise ValueError("a document is listed twice")
        why = self.problems(doc_refs, swap_id)
        if why:
            raise ValueError("; ".join(why))
        for doc_ref in doc_refs:
            self._by_doc[doc_ref] = swap_id

    def tie(self, doc_ref: str, swap_id: str) -> None:
        _need_text(doc_ref=doc_ref, swap_id=swap_id)
        why = self.problem(doc_ref, swap_id)
        if why:
            raise ValueError(why)
        self._by_doc[doc_ref] = swap_id

    def release(self, swap_id: str) -> Optional[str]:
        """Free the whole lot of a swap whose late boxes repaid the loan.

        Returns the first document freed, if any; `release_all` returns them all."""
        docs = self.release_all(swap_id)
        return docs[0] if docs else None

    def release_all(self, swap_id: str) -> tuple[str, ...]:
        docs = self.docs_for(swap_id)
        for doc_ref in docs:
            del self._by_doc[doc_ref]
        return docs

    def __len__(self) -> int:
        return len(self._by_doc)


def _match_detail(order: Order, doc: TransportDoc, tonnes_tolerance: float) -> list[str]:
    gaps = []
    for name in ("booking", "consignee", "producer", "plant", "grade"):
        want, got = getattr(order, name), getattr(doc, name)
        if want.strip().casefold() != got.strip().casefold():
            gaps.append(f"{name} {got!r} on the document, {want!r} on the order")
    if doc.teu != order.teu:
        gaps.append(f"{doc.teu} TEU on the document, {order.teu} on the order")
    if abs(doc.tonnes - order.tonnes) > order.tonnes * tonnes_tolerance + 1e-9:
        gaps.append(f"{doc.tonnes:g} t on the document, {order.tonnes:g} t on the order")
    return gaps


def check_collateral(swap_id: str, order: Order, doc: TransportDoc, register: LotRegister,
                     interests: list[SecurityInterest] = (), bind_day: int = BIND_DAY,
                     tonnes_tolerance: float = 0.0) -> CollateralResult:
    """Run all four checks. Does not change the register; `bind` does."""
    _need_text(swap_id=swap_id)
    if not 0 <= tonnes_tolerance < 1:
        raise ValueError("tonnes_tolerance must be at least 0 and below 1")
    findings = []

    gaps = _match_detail(order, doc, tonnes_tolerance)
    findings.append(Finding(CHECK_MATCH, not gaps,
                            "; ".join(gaps) if gaps else
                            f"{doc.kind} {doc.doc_ref} matches booking {order.booking}"))

    holds = doc.holder.strip().casefold() == order.consignee.strip().casefold()
    findings.append(Finding(CHECK_HOLDER, holds,
                            f"{order.consignee} holds the original {doc.kind}" if holds else
                            f"{doc.holder} holds the original {doc.kind}, not {order.consignee}"))

    live = [i for i in interests if i.doc_ref == doc.doc_ref and i.in_force_on(bind_day)]
    findings.append(Finding(CHECK_FREE, not live,
                            "; ".join(f"{i.holder} holds a {i.kind} over {doc.doc_ref}" for i in live)
                            if live else f"no security interest over {doc.doc_ref} on day {bind_day:+d}"))

    why = register.problem(doc.doc_ref, swap_id)
    findings.append(Finding(CHECK_ONE, why is None,
                            why or f"{doc.doc_ref} is tied to no other swap"))
    return CollateralResult(swap_id, doc.doc_ref, tuple(findings), (doc.doc_ref,))


def bind(swap_id: str, order: Order, doc: TransportDoc, register: LotRegister,
         interests: list[SecurityInterest] = (), bind_day: int = BIND_DAY,
         tonnes_tolerance: float = 0.0) -> CollateralResult:
    """Check, and tie the lot to the swap only if every check passes."""
    result = check_collateral(swap_id, order, doc, register, interests, bind_day, tonnes_tolerance)
    if result.binds:
        register.tie(doc.doc_ref, swap_id)
    return result


PLURALS = {"bill of lading": "bills of lading", "delivery order": "delivery orders"}
IDENTITY_FIELDS = ("booking", "consignee", "producer", "plant", "grade")


def _all(n: int) -> str:
    return "both" if n == 2 else f"all {n}"


def _same(a: str, b: str) -> bool:
    return a.strip().casefold() == b.strip().casefold()


def _split_match(order: Order, docs, tonnes_tolerance: float) -> list[str]:
    gaps = []
    seen = set()
    for doc in docs:
        if doc.doc_ref in seen:
            gaps.append(f"{doc.doc_ref} is offered twice")
        seen.add(doc.doc_ref)
        for name in IDENTITY_FIELDS:
            want, got = getattr(order, name), getattr(doc, name)
            if not _same(want, got):
                gaps.append(f"{doc.doc_ref}: {name} {got!r} on the document, {want!r} on the order")
    vessels = {}
    for doc in docs:
        if doc.vessel.strip():
            vessels.setdefault(doc.vessel.strip().casefold(), doc.vessel.strip())
    if len(vessels) > 1:
        gaps.append(f"documents name more than one vessel ({', '.join(sorted(vessels.values()))}); "
                    "boxes on different vessels may repay on different days, not handled")
    teu = sum(d.teu for d in docs)
    tonnes = sum(d.tonnes for d in docs)
    if teu != order.teu:
        gaps.append(f"documents carry {teu} TEU together, the order {order.teu}")
    if abs(tonnes - order.tonnes) > order.tonnes * tonnes_tolerance + 1e-9:
        gaps.append(f"documents carry {tonnes:g} t together, the order {order.tonnes:g} t")
    return gaps


def check_split(swap_id: str, order: Order, docs, register: LotRegister,
                interests: list[SecurityInterest] = (), bind_day: int = BIND_DAY,
                tonnes_tolerance: float = 0.0) -> CollateralResult:
    """The four checks over every document that together carry the order.

    One document gives exactly the result of `check_collateral`. Does not change
    the register; `bind_split` does."""
    docs = tuple(docs)
    if not docs:
        raise ValueError("at least one document must be given")
    for doc in docs:
        if not isinstance(doc, TransportDoc):
            raise ValueError("every document must be a TransportDoc")
    if len(docs) == 1:
        return check_collateral(swap_id, order, docs[0], register, interests, bind_day,
                                tonnes_tolerance)
    _need_text(swap_id=swap_id)
    if not 0 <= tonnes_tolerance < 1:
        raise ValueError("tonnes_tolerance must be at least 0 and below 1")
    refs = tuple(dict.fromkeys(d.doc_ref for d in docs))   # unique, in order
    label = ", ".join(refs)
    kinds = {d.kind for d in docs}
    what = (f"{len(docs)} {PLURALS[docs[0].kind]}" if len(kinds) == 1 else f"{len(docs)} documents")
    findings = []

    gaps = _split_match(order, docs, tonnes_tolerance)
    findings.append(Finding(CHECK_MATCH, not gaps,
                            "; ".join(gaps) if gaps else
                            f"{what} ({label}) together match booking {order.booking}: "
                            f"{order.teu} TEU, {order.tonnes:g} t"))

    others = [d for d in docs if not _same(d.holder, order.consignee)]
    findings.append(Finding(CHECK_HOLDER, not others,
                            "; ".join(f"{d.holder} holds the original {d.kind} {d.doc_ref}, "
                                      f"not {order.consignee}" for d in others) if others else
                            f"{order.consignee} holds the originals of {_all(len(docs))} documents"))

    live = [i for i in interests if i.doc_ref in refs and i.in_force_on(bind_day)]
    findings.append(Finding(CHECK_FREE, not live,
                            "; ".join(f"{i.holder} holds a {i.kind} over {i.doc_ref}" for i in live)
                            if live else f"no security interest over {label} on day {bind_day:+d}"))

    why = register.problems(refs, swap_id)
    findings.append(Finding(CHECK_ONE, not why,
                            "; ".join(why) if why else
                            f"none of {label} is tied to another swap; {_all(len(refs))} "
                            "would back this swap together"))
    return CollateralResult(swap_id, label, tuple(findings), refs)


def bind_split(swap_id: str, order: Order, docs, register: LotRegister,
               interests: list[SecurityInterest] = (), bind_day: int = BIND_DAY,
               tonnes_tolerance: float = 0.0) -> CollateralResult:
    """Check, and tie every document to the swap only if every check passes."""
    result = check_split(swap_id, order, docs, register, interests, bind_day, tonnes_tolerance)
    if result.binds:
        register.tie_all(result.doc_refs, swap_id)
    return result


def format_result(result: CollateralResult) -> str:
    head = (f"Swap {result.swap_id}, lot {result.doc_ref}: "
            + ("LOAN MAY BIND" if result.binds else "LOAN DOES NOT BIND"))
    lines = [head]
    for f in result.findings:
        lines.append(f"  [{'pass' if f.passed else 'FAIL'}] {f.check}: {f.detail}")
    return "\n".join(lines)


# Mock data for the command line run. Invented; tonnes are not from any real shipment.
PLANT = "Demo Plant BV"
ORDER = Order("BK-DEMO-001", PLANT, "SABIC", "Geleen", "PP 575P", 40, 960)


def mock_doc(**changes) -> TransportDoc:
    base = dict(doc_ref="BL-DEMO-001", kind="bill of lading", booking=ORDER.booking,
                consignee=PLANT, holder=PLANT, producer="SABIC", plant="Geleen",
                grade="PP 575P", teu=40, tonnes=960, vessel="MV DEMO")
    base.update(changes)
    return TransportDoc(**base)


def scenarios() -> list[tuple[str, CollateralResult]]:
    """Five mock cases, run against one shared register in order."""
    reg = LotRegister()
    doc = mock_doc()
    out = [("Clean lot", bind("SW-1", ORDER, doc, reg))]
    out.append(("Same lot offered for a second swap", bind("SW-2", ORDER, doc, reg)))
    out.append(("Document shows another grade and fewer tonnes",
                bind("SW-3", ORDER, mock_doc(doc_ref="BL-DEMO-003", grade="PP 571P", tonnes=900), reg)))
    out.append(("Bank holds the originals under a letter of credit",
                bind("SW-4", ORDER, mock_doc(doc_ref="BL-DEMO-004", holder="Demo Bank"), reg,
                     [SecurityInterest("BL-DEMO-004", "Demo Bank", "letter of credit")])))
    out.append(("Earlier pledge released before the bind day",
                bind("SW-5", ORDER, mock_doc(doc_ref="BL-DEMO-005"), reg,
                     [SecurityInterest("BL-DEMO-005", "Demo Bank", "bank pledge", released_on=-20)])))
    return out


def split_scenarios() -> list[tuple[str, CollateralResult]]:
    """Five mock split shipments: the 40 TEU order under two bills of lading."""
    reg = LotRegister()
    a = mock_doc(doc_ref="BL-SPLIT-A", teu=25, tonnes=600)
    b = mock_doc(doc_ref="BL-SPLIT-B", teu=15, tonnes=360)
    out = [("Split: two clean bills of lading, 25 + 15 TEU", bind_split("SP-1", ORDER, (a, b), reg))]
    out.append(("Split: only one of the two bills offered",
                bind_split("SP-2", ORDER, (mock_doc(doc_ref="BL-SPLIT-C", teu=25, tonnes=600),), reg)))
    out.append(("Split: second bill pledged to a bank",
                bind_split("SP-3", ORDER, (mock_doc(doc_ref="BL-SPLIT-D", teu=25, tonnes=600),
                                           mock_doc(doc_ref="BL-SPLIT-E", teu=15, tonnes=360)), reg,
                           [SecurityInterest("BL-SPLIT-E", "Demo Bank", "bank pledge")])))
    out.append(("Split: the two bills name different vessels",
                bind_split("SP-4", ORDER, (mock_doc(doc_ref="BL-SPLIT-F", teu=25, tonnes=600),
                                           mock_doc(doc_ref="BL-SPLIT-G", teu=15, tonnes=360,
                                                    vessel="MV OTHER")), reg)))
    out.append(("Split: one bill already backs swap SP-1",
                bind_split("SP-5", ORDER, (mock_doc(doc_ref="BL-SPLIT-H", teu=25, tonnes=600), b), reg)))
    return out


def report() -> str:
    lines = [BANNER, ""]
    for title, result in scenarios() + split_scenarios():
        lines += [f"{title}", format_result(result), ""]
    lines.append("The loan binds only when all four checks pass. Rules and tolerance are "
                 "assumptions for the lender and counsel to set.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
