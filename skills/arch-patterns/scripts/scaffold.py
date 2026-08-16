#!/usr/bin/env python3
"""Scaffold a Python/FastAPI project skeleton for a given architecture pattern.

Usage:
    python scaffold.py --list
    python scaffold.py <pattern> <project_name> [--out DIR] [--reflex] [--force]

Patterns: layered | modular-monolith | hexagonal | clean | cqrs-es | microkernel |
          pipes-filters | doma-gateway

Each skeleton is importable and runnable with `uvicorn <pkg>.main:app` after
`pip install fastapi uvicorn` (plus `reflex` when --reflex). Tests run with plain
`pytest` and need no infrastructure. Every skeleton ships a README explaining the
boundaries and (where it applies) an `.importlinter` contract plus a `boundaries.json`
usable by check_boundaries.py.
"""
from __future__ import annotations
import argparse, json, os, sys, textwrap
from pathlib import Path

PATTERNS = {
    "layered": "Layered monolith: presentation -> service -> domain -> persistence",
    "modular-monolith": "Modular monolith: vertical modules per domain + in-process bus + import-linter",
    "hexagonal": "Ports & Adapters: core (domain/ports/use_cases) + adapters (api, ui, persistence, messaging)",
    "clean": "Clean Architecture: domain / application / interface_adapters / infrastructure",
    "cqrs-es": "CQRS + Event Sourcing: aggregate, event store, projections, commands vs queries",
    "microkernel": "Microkernel: kernel + Protocol contract + plugins via entry points",
    "pipes-filters": "Pipes & Filters: composable Iterable->Iterable filters + FastAPI streaming",
    "doma-gateway": "DOMA: domain gateway + layer rules + logic/data extensions",
}


def w(root: Path, rel: str, content: str, force: bool):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and not force:
        raise SystemExit(f"refusing to overwrite {p} (use --force)")
    p.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def common(root: Path, pkg: str, pattern: str, force: bool, reflex: bool, boundaries: dict | None):
    w(root, "pyproject.toml", f'''
    [project]
    name = "{pkg}"
    version = "0.1.0"
    requires-python = ">=3.11"
    dependencies = ["fastapi", "uvicorn"{', "reflex"' if reflex else ''}]
    [project.optional-dependencies]
    dev = ["pytest", "httpx", "import-linter"]
    ''', force)
    w(root, "tests/__init__.py", "", force)
    if boundaries:
        w(root, "boundaries.json", json.dumps(boundaries, indent=2, ensure_ascii=False) + "\n", force)
    w(root, ".gitignore", "__pycache__/\n*.pyc\n.venv/\n.web/\n", force)


# ---------------------------------------------------------------- layered
def layered(root: Path, pkg: str, force: bool, reflex: bool):
    w(root, f"{pkg}/__init__.py", "", force)
    w(root, f"{pkg}/main.py", f'''
    """Presentation layer (FastAPI). Talks to the service layer only."""
    from fastapi import Depends, FastAPI, HTTPException
    from {pkg}.services import ItemService
    from {pkg}.repositories import InMemoryItemRepo

    app = FastAPI(title="{pkg} - layered")
    _repo = InMemoryItemRepo()

    def get_service() -> ItemService:
        return ItemService(_repo)

    @app.post("/items/{{item_id}}")
    def create(item_id: str, name: str, svc: ItemService = Depends(get_service)):
        return svc.create(item_id, name)

    @app.get("/items/{{item_id}}")
    def read(item_id: str, svc: ItemService = Depends(get_service)):
        try:
            return svc.get(item_id)
        except LookupError as e:
            raise HTTPException(404, str(e))
    ''', force)
    w(root, f"{pkg}/services.py", '''
    """Service / application layer: orchestrates rules and persistence."""
    from .domain import Item
    from .repositories import ItemRepository

    class ItemService:
        def __init__(self, repo: ItemRepository):
            self.repo = repo

        def create(self, item_id: str, name: str) -> dict:
            item = Item(item_id, name)
            item.validate()
            self.repo.save(item)
            return item.to_dict()

        def get(self, item_id: str) -> dict:
            item = self.repo.get(item_id)
            if item is None:
                raise LookupError(f"Item {item_id} not found")
            return item.to_dict()
    ''', force)
    w(root, f"{pkg}/domain.py", '''
    """Domain layer: entities and rules. No framework dependencies."""
    from dataclasses import dataclass

    @dataclass
    class Item:
        id: str
        name: str

        def validate(self) -> None:
            if not self.name.strip():
                raise ValueError("empty name")

        def to_dict(self) -> dict:
            return {"id": self.id, "name": self.name}
    ''', force)
    w(root, f"{pkg}/repositories.py", '''
    """Persistence layer. Swap InMemoryItemRepo for Mongo/SQL without touching the layers above."""
    from typing import Protocol
    from .domain import Item

    class ItemRepository(Protocol):
        def get(self, item_id: str) -> Item | None: ...
        def save(self, item: Item) -> None: ...

    class InMemoryItemRepo:
        def __init__(self):
            self._data: dict[str, Item] = {}
        def get(self, item_id: str) -> Item | None:
            return self._data.get(item_id)
        def save(self, item: Item) -> None:
            self._data[item.id] = item
    ''', force)
    w(root, "tests/test_service.py", f'''
    from {pkg}.services import ItemService
    from {pkg}.repositories import InMemoryItemRepo

    def test_create_and_get():
        svc = ItemService(InMemoryItemRepo())
        svc.create("1", "one")
        assert svc.get("1")["name"] == "one"
    ''', force)
    if reflex:
        w(root, f"{pkg}_ui/{pkg}_ui.py", f'''
        """Reflex in the same process: the UI calls the service layer directly."""
        import reflex as rx
        from {pkg}.services import ItemService
        from {pkg}.repositories import InMemoryItemRepo

        _svc = ItemService(InMemoryItemRepo())

        class State(rx.State):
            item_id: str = ""
            result: str = ""
            def search(self):
                try:
                    self.result = str(_svc.get(self.item_id))
                except LookupError as e:
                    self.result = str(e)

        def index():
            return rx.vstack(rx.input(on_change=State.set_item_id), rx.button("Search", on_click=State.search), rx.text(State.result))

        app = rx.App()
        app.add_page(index)
        ''', force)
    boundaries = {"kind": "layers", "root": pkg, "layers": ["main", "services", "repositories", "domain"],
                  "notes": "main -> services -> repositories -> domain; domain imports nothing from the package"}
    common(root, pkg, "layered", force, reflex, boundaries)
    w(root, "README.md", f'''
    # {pkg} — Layered monolith
    Layers: `main.py` (presentation) → `services.py` → `domain.py` / `repositories.py`.
    Rule: each layer only imports the one below it; `domain.py` imports nothing from the package.
    Verify: `python check_boundaries.py {pkg} --rules boundaries.json`.
    Run: `uvicorn {pkg}.main:app --reload` - Tests: `pytest`.
    ''', force)


# ---------------------------------------------------------------- modular monolith
def modular(root: Path, pkg: str, force: bool, reflex: bool):
    mods = ["policies", "payments"]
    entities = {"policies": "Policy", "payments": "Payment"}
    w(root, f"{pkg}/__init__.py", "", force)
    w(root, f"{pkg}/shared/__init__.py", "", force)
    w(root, f"{pkg}/shared/events.py", '''
    """In-process event bus. The only channel between modules besides their public API."""
    from collections import defaultdict
    from typing import Callable
    _subs: dict[str, list[Callable[[dict], None]]] = defaultdict(list)

    def subscribe(event: str, handler: Callable[[dict], None]) -> None:
        _subs[event].append(handler)

    def publish(event: str, payload: dict) -> None:
        for h in list(_subs[event]):
            h(payload)

    def reset() -> None:  # for tests
        _subs.clear()
    ''', force)
    for m in mods:
        w(root, f"{pkg}/{m}/__init__.py", f'"""Module {m}. Public surface: api.router and the events it publishes."""\n', force)
        w(root, f"{pkg}/{m}/domain.py", f'''
        from dataclasses import dataclass

        @dataclass
        class {entities[m]}:
            id: str
            status: str = "PENDING"
        ''', force)
        w(root, f"{pkg}/{m}/repo.py", '''
        _store: dict[str, dict] = {}
        def save(obj_id: str, data: dict) -> None: _store[obj_id] = data
        def get(obj_id: str) -> dict | None: return _store.get(obj_id)
        ''', force)
    w(root, f"{pkg}/payments/api.py", f'''
    from fastapi import APIRouter
    from {pkg}.shared.events import publish
    from . import repo

    router = APIRouter(prefix="/payments", tags=["payments"])

    @router.post("/{{ref}}/confirm")
    def confirm(ref: str, policy_id: str):
        repo.save(ref, {{"ref": ref, "policy_id": policy_id, "status": "CONFIRMED"}})
        publish("PaymentConfirmed", {{"ref": ref, "policy_id": policy_id}})
        return {{"ok": True}}
    ''', force)
    w(root, f"{pkg}/policies/api.py", f'''
    from fastapi import APIRouter, HTTPException
    from {pkg}.shared.events import subscribe
    from . import repo

    router = APIRouter(prefix="/policies", tags=["policies"])

    def _on_payment_confirmed(payload: dict) -> None:
        repo.save(payload["policy_id"], {{"id": payload["policy_id"], "status": "ACTIVE"}})

    subscribe("PaymentConfirmed", _on_payment_confirmed)

    @router.get("/{{policy_id}}")
    def get_policy(policy_id: str):
        p = repo.get(policy_id)
        if p is None:
            raise HTTPException(404)
        return p
    ''', force)
    w(root, f"{pkg}/main.py", f'''
    from fastapi import FastAPI
    from {pkg}.policies.api import router as policies_router
    from {pkg}.payments.api import router as payments_router

    app = FastAPI(title="{pkg} - modular monolith")
    app.include_router(policies_router)
    app.include_router(payments_router)
    ''', force)
    w(root, ".importlinter", f'''
    [importlinter]
    root_package = {pkg}

    [importlinter:contract:independent-modules]
    name = Modules do not import other modules' internals
    type = independence
    modules =
        {pkg}.policies
        {pkg}.payments
    ''', force)
    w(root, "tests/test_modules.py", f'''
    from fastapi.testclient import TestClient
    from {pkg}.main import app

    def test_payment_activates_policy():
        c = TestClient(app)
        assert c.post("/payments/r1/confirm", params={{"policy_id": "P1"}}).status_code == 200
        assert c.get("/policies/P1").json()["status"] == "ACTIVE"
    ''', force)
    boundaries = {"kind": "independence", "root": pkg, "modules": mods, "shared": [f"{pkg}.shared"]}
    common(root, pkg, "modular-monolith", force, reflex, boundaries)
    w(root, "README.md", f'''
    # {pkg} — Modular monolith
    Vertical modules: `{"`, `".join(mods)}` with `api.py` (public), `domain.py`, `repo.py` (private).
    Communication between modules: only the public `api` or `shared/events.py`. Never import `other_module.repo`.
    Verify: `lint-imports` (import-linter) or `python check_boundaries.py {pkg} --rules boundaries.json`.
    Extracting a module into a service = move the folder and swap the in-process bus for a broker.
    ''', force)


# ---------------------------------------------------------------- hexagonal
def hexagonal(root: Path, pkg: str, force: bool, reflex: bool):
    w(root, f"{pkg}/__init__.py", "", force)
    w(root, f"{pkg}/core/__init__.py", "", force)
    w(root, f"{pkg}/core/domain.py", '''
    """Pure domain. Importing FastAPI, PyMongo, Reflex, etc. is forbidden here."""
    from dataclasses import dataclass, field
    from enum import Enum

    class Status(str, Enum):
        PENDING = "PENDING"
        ACTIVE = "ACTIVE"

    @dataclass
    class Policy:
        policy_number: str
        status: Status = Status.PENDING
        events: list[dict] = field(default_factory=list)

        def activate(self) -> None:
            if self.status is Status.ACTIVE:
                raise ValueError("The policy is already active")
            self.status = Status.ACTIVE
            self.events.append({"type": "PolicyActivated", "policy_number": self.policy_number})
    ''', force)
    w(root, f"{pkg}/core/ports.py", '''
    """Ports: interfaces defined by the core and implemented by the adapters."""
    from typing import Protocol
    from .domain import Policy

    class PolicyRepository(Protocol):          # secondary (driven) port
        def get(self, policy_number: str) -> Policy | None: ...
        def save(self, policy: Policy) -> None: ...

    class EventPublisher(Protocol):            # secondary (driven) port
        def publish(self, event: dict) -> None: ...
    ''', force)
    w(root, f"{pkg}/core/use_cases.py", '''
    """Use cases = primary (driving) ports."""
    from .domain import Policy
    from .ports import EventPublisher, PolicyRepository

    class ActivatePolicy:
        def __init__(self, repo: PolicyRepository, publisher: EventPublisher):
            self.repo, self.publisher = repo, publisher

        def __call__(self, policy_number: str) -> Policy:
            policy = self.repo.get(policy_number)
            if policy is None:
                raise LookupError("Policy not found")
            policy.activate()
            self.repo.save(policy)
            for e in policy.events:
                self.publisher.publish(e)
            return policy

    class CreatePolicy:
        def __init__(self, repo: PolicyRepository):
            self.repo = repo
        def __call__(self, policy_number: str) -> Policy:
            p = Policy(policy_number)
            self.repo.save(p)
            return p
    ''', force)
    w(root, f"{pkg}/adapters/__init__.py", "", force)
    w(root, f"{pkg}/adapters/persistence.py", f'''
    """Secondary persistence adapters. Add MongoPolicyRepo/SqlPolicyRepo here."""
    from {pkg}.core.domain import Policy

    class InMemoryPolicyRepo:
        def __init__(self):
            self._data: dict[str, Policy] = {{}}
        def get(self, policy_number: str) -> Policy | None:
            return self._data.get(policy_number)
        def save(self, policy: Policy) -> None:
            self._data[policy.policy_number] = policy
    ''', force)
    w(root, f"{pkg}/adapters/messaging.py", '''
    """Secondary messaging adapter. Replace with RabbitMQ/Redis Streams."""
    class LogPublisher:
        def __init__(self):
            self.published: list[dict] = []
        def publish(self, event: dict) -> None:
            self.published.append(event)
            print("EVENT", event)
    ''', force)
    w(root, f"{pkg}/adapters/api.py", f'''
    """Primary REST adapter (FastAPI). Only translates HTTP <-> use cases."""
    from fastapi import FastAPI, HTTPException
    from {pkg}.core.use_cases import ActivatePolicy, CreatePolicy

    def build_app(create: CreatePolicy, activate: ActivatePolicy) -> FastAPI:
        app = FastAPI(title="{pkg} - hexagonal")

        @app.post("/policies/{{number}}")
        def create_ep(number: str):
            return {{"policy_number": create(number).policy_number}}

        @app.post("/policies/{{number}}/activate")
        def activate_ep(number: str):
            try:
                return {{"policy_number": number, "status": activate(number).status}}
            except LookupError as e:
                raise HTTPException(404, str(e))
            except ValueError as e:
                raise HTTPException(409, str(e))
        return app
    ''', force)
    w(root, f"{pkg}/main.py", f'''
    """Composition root: the concrete adapters are chosen here, and only here."""
    from {pkg}.adapters.api import build_app
    from {pkg}.adapters.messaging import LogPublisher
    from {pkg}.adapters.persistence import InMemoryPolicyRepo
    from {pkg}.core.use_cases import ActivatePolicy, CreatePolicy

    repo = InMemoryPolicyRepo()
    publisher = LogPublisher()
    app = build_app(CreatePolicy(repo), ActivatePolicy(repo, publisher))
    ''', force)
    if reflex:
        w(root, f"{pkg}/adapters/ui_reflex.py", f'''
        """Primary UI adapter (Reflex): drives the same use cases as the API."""
        import reflex as rx
        from {pkg}.main import repo, publisher
        from {pkg}.core.use_cases import ActivatePolicy

        _activate = ActivatePolicy(repo, publisher)

        class State(rx.State):
            number: str = ""
            msg: str = ""
            def activate(self):
                try:
                    self.msg = _activate(self.number).status
                except Exception as e:
                    self.msg = str(e)

        def index():
            return rx.vstack(rx.input(on_change=State.set_number), rx.button("Activate", on_click=State.activate), rx.text(State.msg))

        app = rx.App()
        app.add_page(index)
        ''', force)
    w(root, "tests/test_use_cases.py", f'''
    from {pkg}.core.domain import Status, Policy
    from {pkg}.core.use_cases import ActivatePolicy
    from {pkg}.adapters.persistence import InMemoryPolicyRepo
    from {pkg}.adapters.messaging import LogPublisher

    def test_activate_publishes_event():
        repo, pub = InMemoryPolicyRepo(), LogPublisher()
        repo.save(Policy("P-1"))
        assert ActivatePolicy(repo, pub)("P-1").status is Status.ACTIVE
        assert pub.published[0]["type"] == "PolicyActivated"
    ''', force)
    w(root, ".importlinter", f'''
    [importlinter]
    root_package = {pkg}

    [importlinter:contract:core-does-not-depend-on-adapters]
    name = The core imports neither adapters nor frameworks
    type = forbidden
    source_modules =
        {pkg}.core
    forbidden_modules =
        {pkg}.adapters
        {pkg}.main
        fastapi
        pymongo
        reflex
    ''', force)
    boundaries = {"kind": "forbidden", "root": pkg, "rules": [
        {"source": f"{pkg}.core", "forbidden": [f"{pkg}.adapters", f"{pkg}.main", "fastapi", "pymongo", "reflex", "sqlalchemy"]}]}
    common(root, pkg, "hexagonal", force, reflex, boundaries)
    w(root, "README.md", f'''
    # {pkg} — Hexagonal (Ports & Adapters)
    - `core/domain.py` entities and rules - `core/ports.py` interfaces (Protocol) - `core/use_cases.py` input ports.
    - `adapters/` implementations: `api.py` (FastAPI, driving), `persistence.py`, `messaging.py` (driven){', `ui_reflex.py` (driving)' if reflex else ''}.
    - `main.py` composition root: the only place that knows the concrete adapters.
    Rule: `core` imports neither `adapters` nor frameworks (see `.importlinter` / `boundaries.json`).
    Core tests run in milliseconds with `InMemoryPolicyRepo`.
    ''', force)


# ---------------------------------------------------------------- clean
def clean(root: Path, pkg: str, force: bool, reflex: bool):
    w(root, f"{pkg}/__init__.py", "", force)
    for d in ["domain", "application", "application/ports", "application/dto", "application/use_cases",
              "interface_adapters", "interface_adapters/controllers", "interface_adapters/repositories",
              "infrastructure", "infrastructure/web"]:
        w(root, f"{pkg}/{d}/__init__.py", "", force)
    w(root, f"{pkg}/domain/policy.py", '''
    from dataclasses import dataclass
    from enum import Enum

    class Status(str, Enum):
        PENDING = "PENDING"; ACTIVE = "ACTIVE"

    @dataclass
    class Policy:
        policy_number: str
        status: Status = Status.PENDING
        def activate(self, by: str) -> None:
            if self.status is Status.ACTIVE:
                raise ValueError("already active")
            self.status = Status.ACTIVE
    ''', force)
    w(root, f"{pkg}/application/ports/policy_repository.py", f'''
    from typing import Protocol
    from {pkg}.domain.policy import Policy
    class PolicyRepository(Protocol):
        def get(self, policy_number: str) -> Policy | None: ...
        def save(self, policy: Policy) -> None: ...
    ''', force)
    w(root, f"{pkg}/application/dto/activate_policy.py", '''
    from dataclasses import dataclass
    @dataclass(frozen=True)
    class ActivatePolicyInput:
        policy_number: str
        user: str
    @dataclass(frozen=True)
    class ActivatePolicyOutput:
        policy_number: str
        status: str
    ''', force)
    w(root, f"{pkg}/application/use_cases/activate_policy.py", f'''
    from {pkg}.application.dto.activate_policy import ActivatePolicyInput, ActivatePolicyOutput
    from {pkg}.application.ports.policy_repository import PolicyRepository
    from {pkg}.domain.policy import Policy

    class ActivatePolicyUseCase:
        def __init__(self, repo: PolicyRepository):
            self.repo = repo
        def execute(self, inp: ActivatePolicyInput) -> ActivatePolicyOutput:
            policy = self.repo.get(inp.policy_number) or Policy(inp.policy_number)
            policy.activate(by=inp.user)
            self.repo.save(policy)
            return ActivatePolicyOutput(policy.policy_number, policy.status.value)
    ''', force)
    w(root, f"{pkg}/interface_adapters/repositories/memory_policy_repository.py", f'''
    from {pkg}.domain.policy import Policy
    class MemoryPolicyRepository:
        def __init__(self): self._d: dict[str, Policy] = {{}}
        def get(self, policy_number: str): return self._d.get(policy_number)
        def save(self, policy: Policy): self._d[policy.policy_number] = policy
    ''', force)
    w(root, f"{pkg}/interface_adapters/controllers/policy_controller.py", f'''
    from pydantic import BaseModel
    from {pkg}.application.dto.activate_policy import ActivatePolicyInput
    from {pkg}.application.use_cases.activate_policy import ActivatePolicyUseCase

    class ActivatePolicyResponse(BaseModel):
        policy_number: str
        status: str

    class PolicyController:
        def __init__(self, uc: ActivatePolicyUseCase): self.uc = uc
        def activate(self, number: str, user: str) -> ActivatePolicyResponse:
            out = self.uc.execute(ActivatePolicyInput(number, user))
            return ActivatePolicyResponse(policy_number=out.policy_number, status=out.status)
    ''', force)
    w(root, f"{pkg}/infrastructure/di.py", f'''
    from {pkg}.application.use_cases.activate_policy import ActivatePolicyUseCase
    from {pkg}.interface_adapters.controllers.policy_controller import PolicyController
    from {pkg}.interface_adapters.repositories.memory_policy_repository import MemoryPolicyRepository
    _repo = MemoryPolicyRepository()
    def get_policy_controller() -> PolicyController:
        return PolicyController(ActivatePolicyUseCase(_repo))
    ''', force)
    w(root, f"{pkg}/infrastructure/web/app.py", f'''
    from fastapi import Depends, FastAPI, HTTPException
    from {pkg}.infrastructure.di import get_policy_controller
    from {pkg}.interface_adapters.controllers.policy_controller import ActivatePolicyResponse, PolicyController

    app = FastAPI(title="{pkg} - clean")

    @app.post("/policies/{{number}}/activate", response_model=ActivatePolicyResponse)
    def activate(number: str, ctl: PolicyController = Depends(get_policy_controller)):
        try:
            return ctl.activate(number, user="api")
        except ValueError as e:
            raise HTTPException(409, str(e))
    ''', force)
    w(root, f"{pkg}/main.py", f"from {pkg}.infrastructure.web.app import app  # noqa: F401\n", force)
    w(root, "tests/test_use_case.py", f'''
    from {pkg}.application.dto.activate_policy import ActivatePolicyInput
    from {pkg}.application.use_cases.activate_policy import ActivatePolicyUseCase
    from {pkg}.interface_adapters.repositories.memory_policy_repository import MemoryPolicyRepository

    def test_activate():
        out = ActivatePolicyUseCase(MemoryPolicyRepository()).execute(ActivatePolicyInput("P1", "test"))
        assert out.status == "ACTIVE"
    ''', force)
    w(root, ".importlinter", f'''
    [importlinter]
    root_package = {pkg}

    [importlinter:contract:dependency-rule]
    name = Dependencies point inwards only
    type = layers
    layers =
        {pkg}.infrastructure
        {pkg}.interface_adapters
        {pkg}.application
        {pkg}.domain
    ''', force)
    boundaries = {"kind": "layers", "root": pkg, "layers": ["infrastructure", "interface_adapters", "application", "domain"]}
    common(root, pkg, "clean", force, reflex, boundaries)
    w(root, "README.md", f'''
    # {pkg} — Clean Architecture
    `domain` ← `application` (use cases, ports, DTOs) ← `interface_adapters` (controllers, repos) ← `infrastructure` (FastAPI, DI).
    Dependency rule: inwards only (`layers` contract in `.importlinter`).
    ''', force)


# ---------------------------------------------------------------- cqrs-es
def cqrs(root: Path, pkg: str, force: bool, reflex: bool):
    w(root, f"{pkg}/__init__.py", "", force)
    w(root, f"{pkg}/write/__init__.py", "", force)
    w(root, f"{pkg}/read/__init__.py", "", force)
    w(root, f"{pkg}/write/events.py", '''
    from dataclasses import dataclass
    @dataclass(frozen=True)
    class Event:
        type: str
        data: dict
        version: int
    ''', force)
    w(root, f"{pkg}/write/aggregate.py", '''
    from .events import Event

    class PolicyAggregate:
        def __init__(self, number: str):
            self.number, self.status, self.version, self._new = number, None, 0, []
        # decide
        def create(self, plan: str):
            if self.version: raise ValueError("already exists")
            self._emit("PolicyCreated", {"number": self.number, "plan": plan})
        def activate(self):
            if self.status is None: raise ValueError("does not exist")
            if self.status == "ACTIVE": raise ValueError("already active")
            self._emit("PolicyActivated", {"number": self.number})
        # evolve
        def _apply(self, e: Event):
            if e.type == "PolicyCreated": self.status = "PENDING"
            elif e.type == "PolicyActivated": self.status = "ACTIVE"
            self.version = e.version
        def _emit(self, event_type: str, data: dict):
            e = Event(event_type, data, self.version + 1); self._apply(e); self._new.append(e)
        @classmethod
        def from_history(cls, number: str, history: list[Event]):
            a = cls(number)
            for e in history: a._apply(e)
            return a
        def pending_events(self) -> list[Event]:
            ev, self._new = self._new, []
            return ev
    ''', force)
    w(root, f"{pkg}/write/store.py", '''
    """Append-only event store. In Mongo: unique index (stream, version) for optimistic concurrency."""
    from collections import defaultdict
    from .events import Event

    class ConcurrencyError(Exception): ...

    class InMemoryEventStore:
        def __init__(self):
            self._streams: dict[str, list[Event]] = defaultdict(list)
            self.subscribers = []
        def load(self, stream: str) -> list[Event]:
            return list(self._streams[stream])
        def append(self, stream: str, events: list[Event]) -> None:
            existing = self._streams[stream]
            for e in events:
                if e.version != len(existing) + 1:
                    raise ConcurrencyError(f"{stream}: expected v{len(existing)+1}, got v{e.version}")
                existing.append(e)
                for s in self.subscribers: s(stream, e)
    ''', force)
    w(root, f"{pkg}/read/projections.py", f'''
    """Projectors: build denormalised read models out of the stream."""
    from {pkg}.write.events import Event

    class SummaryProjection:
        def __init__(self): self.rows: dict[str, dict] = {{}}
        def handle(self, stream: str, e: Event) -> None:
            if e.type == "PolicyCreated":
                self.rows[stream] = {{"number": stream, "plan": e.data["plan"], "status": "PENDING"}}
            elif e.type == "PolicyActivated":
                self.rows[stream]["status"] = "ACTIVE"
    ''', force)
    w(root, f"{pkg}/main.py", f'''
    from fastapi import FastAPI, HTTPException
    from {pkg}.write.aggregate import PolicyAggregate
    from {pkg}.write.store import ConcurrencyError, InMemoryEventStore
    from {pkg}.read.projections import SummaryProjection

    app = FastAPI(title="{pkg} - CQRS + ES")
    store, proj = InMemoryEventStore(), SummaryProjection()
    store.subscribers.append(proj.handle)   # in production: async, via bus/outbox

    def _dispatch(number: str, fn):
        agg = PolicyAggregate.from_history(number, store.load(number))
        try:
            fn(agg)
            store.append(number, agg.pending_events())
        except ValueError as e:
            raise HTTPException(409, str(e))
        except ConcurrencyError as e:
            raise HTTPException(409, str(e))
        return {{"version": agg.version}}

    @app.post("/commands/policies/{{number}}/create")       # WRITE
    def cmd_create(number: str, plan: str): return _dispatch(number, lambda a: a.create(plan))

    @app.post("/commands/policies/{{number}}/activate")     # WRITE
    def cmd_activate(number: str): return _dispatch(number, lambda a: a.activate())

    @app.get("/queries/policies/{{number}}")                # READ (never touches the aggregate)
    def qry(number: str):
        row = proj.rows.get(number)
        if row is None: raise HTTPException(404)
        return row

    @app.get("/queries/policies/{{number}}/history")        # audit
    def history(number: str): return [e.__dict__ for e in store.load(number)]
    ''', force)
    w(root, "tests/test_cqrs.py", f'''
    from fastapi.testclient import TestClient
    from {pkg}.main import app

    def test_flow():
        c = TestClient(app)
        assert c.post("/commands/policies/P1/create", params={{"plan": "gold"}}).json()["version"] == 1
        assert c.post("/commands/policies/P1/activate").json()["version"] == 2
        assert c.get("/queries/policies/P1").json()["status"] == "ACTIVE"
        assert c.post("/commands/policies/P1/activate").status_code == 409
        assert len(c.get("/queries/policies/P1/history").json()) == 2
    ''', force)
    boundaries = {"kind": "forbidden", "root": pkg, "rules": [{"source": f"{pkg}.read", "forbidden": [f"{pkg}.write.aggregate", f"{pkg}.write.store"]}]}
    common(root, pkg, "cqrs-es", force, reflex, boundaries)
    w(root, "README.md", f'''
    # {pkg} — CQRS + Event Sourcing
    `write/` aggregate (decide/evolve), events, append-only event store with version control.
    `read/` projections → read models. `read` only knows the events, never the aggregate or the store.
    Endpoints `/commands/*` (writes) and `/queries/*` (reads). Swap InMemoryEventStore for Mongo with a unique index on (stream, version).
    ''', force)


# ---------------------------------------------------------------- microkernel
def microkernel(root: Path, pkg: str, force: bool, reflex: bool):
    w(root, f"{pkg}/__init__.py", "", force)
    w(root, f"{pkg}/kernel/__init__.py", "", force)
    w(root, f"{pkg}/kernel/contract.py", '''
    """Plugin contract. Changing it is a major version change."""
    from typing import Protocol, runtime_checkable

    @runtime_checkable
    class ValidatorPlugin(Protocol):
        name: str
        priority: int
        def validate(self, document: dict) -> list[str]: ...
    ''', force)
    w(root, f"{pkg}/kernel/registry.py", f'''
    """Discovers plugins via entry points (group '{pkg}.validators') and manual registration."""
    from importlib.metadata import entry_points
    from .contract import ValidatorPlugin

    class Kernel:
        def __init__(self, group: str = "{pkg}.validators"):
            self.plugins: list[ValidatorPlugin] = []
            for ep in entry_points(group=group):
                self.register(ep.load()())

        def register(self, plugin: ValidatorPlugin) -> None:
            if not isinstance(plugin, ValidatorPlugin):
                raise TypeError(f"{{plugin!r}} does not satisfy ValidatorPlugin")
            self.plugins.append(plugin)
            self.plugins.sort(key=lambda p: p.priority)

        def run(self, document: dict) -> dict:
            errors = {{p.name: e for p in self.plugins if (e := p.validate(document))}}
            return {{"valid": not errors, "errors": errors, "plugins": [p.name for p in self.plugins]}}
    ''', force)
    w(root, f"{pkg}/plugins/__init__.py", "", force)
    w(root, f"{pkg}/plugins/arithmetic.py", '''
    class ArithmeticValidator:
        name, priority = "arithmetic", 10
        def validate(self, doc: dict) -> list[str]:
            total = sum(i["quantity"] * i["price"] for i in doc.get("items", []))
            return [] if abs(total - doc.get("total", 0)) < 0.01 else [f"total {doc.get('total')} != sum {total:.2f}"]
    ''', force)
    w(root, f"{pkg}/main.py", f'''
    from fastapi import FastAPI
    from {pkg}.kernel.registry import Kernel
    from {pkg}.plugins.arithmetic import ArithmeticValidator

    kernel = Kernel()
    kernel.register(ArithmeticValidator())     # on top of the ones discovered via entry points
    app = FastAPI(title="{pkg} - microkernel")

    @app.post("/validate")
    def validate(document: dict): return kernel.run(document)

    @app.get("/plugins")
    def plugins(): return [p.name for p in kernel.plugins]
    ''', force)
    w(root, "tests/test_kernel.py", f'''
    from {pkg}.kernel.registry import Kernel
    from {pkg}.plugins.arithmetic import ArithmeticValidator

    def test_plugin():
        k = Kernel(group="nope"); k.register(ArithmeticValidator())
        assert k.run({{"items": [{{"quantity": 2, "price": 5}}], "total": 10}})["valid"]
        assert not k.run({{"items": [{{"quantity": 2, "price": 5}}], "total": 11}})["valid"]
    ''', force)
    boundaries = {"kind": "forbidden", "root": pkg, "rules": [{"source": f"{pkg}.kernel", "forbidden": [f"{pkg}.plugins"]}]}
    common(root, pkg, "microkernel", force, reflex, boundaries)
    w(root, "README.md", f'''
    # {pkg} — Microkernel
    `kernel/contract.py` (Protocol) + `kernel/registry.py` (entry-point discovery + registration).
    External plugins: in their `pyproject.toml` → `[project.entry-points."{pkg}.validators"] name = "module:Class"`.
    Rule: the kernel never imports concrete plugins.
    ''', force)


# ---------------------------------------------------------------- pipes & filters
def pipes(root: Path, pkg: str, force: bool, reflex: bool):
    w(root, f"{pkg}/__init__.py", "", force)
    w(root, f"{pkg}/contracts.py", '''
    """Data contracts between stages: the only dependency shared by the filters."""
    from dataclasses import dataclass
    @dataclass(frozen=True)
    class Line:
        text: str
    @dataclass(frozen=True)
    class Item:
        description: str
        quantity: int
        price: float
    ''', force)
    w(root, f"{pkg}/filters.py", '''
    """Every filter: Iterable[In] -> Iterable[Out]. No shared state, testable in isolation."""
    from typing import Iterable
    from .contracts import Item, Line

    def read_lines(text: str) -> Iterable[Line]:
        for l in text.splitlines():
            if l.strip(): yield Line(l.strip())

    def extract_items(lines: Iterable[Line]) -> Iterable[Item]:
        for l in lines:
            parts = l.text.rsplit(" ", 2)         # "description quantity price"
            if len(parts) == 3:
                try: yield Item(parts[0], int(parts[1]), float(parts[2]))
                except ValueError: continue

    def validate(items: Iterable[Item]) -> Iterable[Item]:
        for it in items:
            if it.quantity > 0 and it.price >= 0: yield it

    def enrich(items: Iterable[Item], catalog: dict[str, str]) -> Iterable[dict]:
        for it in items:
            yield {**it.__dict__, "code": catalog.get(it.description.upper())}
    ''', force)
    w(root, f"{pkg}/pipeline.py", '''
    from .filters import enrich, extract_items, read_lines, validate

    def process(text: str, catalog: dict[str, str]) -> list[dict]:
        return list(enrich(validate(extract_items(read_lines(text))), catalog))
    ''', force)
    w(root, f"{pkg}/main.py", f'''
    import json
    from fastapi import FastAPI, UploadFile
    from fastapi.responses import StreamingResponse
    from {pkg}.filters import enrich, extract_items, read_lines, validate

    app = FastAPI(title="{pkg} - pipes & filters")
    CATALOG = {{"PARACETAMOL": "MED-001"}}

    @app.post("/process")
    async def process(file: UploadFile):
        text = (await file.read()).decode()
        def gen():
            for row in enrich(validate(extract_items(read_lines(text))), CATALOG):
                yield json.dumps(row) + "\\n"
        return StreamingResponse(gen(), media_type="application/x-ndjson")
    ''', force)
    w(root, "tests/test_pipeline.py", f'''
    from {pkg}.pipeline import process
    def test_pipeline():
        out = process("paracetamol 2 1.5\\ngarbage\\nibuprofen 0 3", {{"PARACETAMOL": "MED-001"}})
        assert out == [{{"description": "paracetamol", "quantity": 2, "price": 1.5, "code": "MED-001"}}]
    ''', force)
    common(root, pkg, "pipes-filters", force, reflex, None)
    w(root, "README.md", f'''
    # {pkg} — Pipes & Filters
    `contracts.py` (dataclasses between stages) - `filters.py` (Iterable → Iterable) - `pipeline.py` (composition) - `main.py` (NDJSON streaming).
    Adding a stage = one new function; parallelising = move a filter to a queue-backed worker.
    ''', force)


# ---------------------------------------------------------------- doma gateway
def doma(root: Path, pkg: str, force: bool, reflex: bool):
    w(root, f"{pkg}/__init__.py", "", force)
    w(root, f"{pkg}/platform/__init__.py", "", force)
    w(root, f"{pkg}/platform/layers.py", '''
    """Layer design: a domain may only depend on lower layers."""
    LAYERS = ["infrastructure", "business", "product", "presentation", "edge"]

    def layer_of(domain_id: str) -> int:
        return LAYERS.index(domain_id.split(".")[0])

    def assert_can_call(caller: str, callee: str) -> None:
        if caller.split(".")[0] == callee.split(".")[0]:
            return
        if layer_of(caller) <= layer_of(callee):
            raise PermissionError(f"{caller} cannot depend on {callee}: violates layer design")
    ''', force)
    w(root, f"{pkg}/domains/__init__.py", "", force)
    w(root, f"{pkg}/domains/pricing/__init__.py", "", force)
    w(root, f"{pkg}/domains/pricing/extensions.py", '''
    """Extension points of the domain (logic + data). Other teams register here."""
    from typing import Any, Callable
    DataExt = dict[str, Any]
    Validator = Callable[[dict], list[str]]
    validators: list[Validator] = []

    def logic_extension(fn: Validator) -> Validator:
        validators.append(fn)
        return fn
    ''', force)
    w(root, f"{pkg}/domains/pricing/internal.py", '''
    """Internal services of the domain: NOBODY outside the domain calls them directly."""
    def base_premium(plan: str, age: int) -> float:
        return {"gold": 30.0, "silver": 20.0}.get(plan, 10.0) * (1.5 if age > 60 else 1.0)
    def discount_factor(plan: str) -> float:
        return 0.9 if plan == "gold" else 1.0
    ''', force)
    w(root, f"{pkg}/domains/pricing/gateway.py", f'''
    """Gateway of the Pricing domain (business layer): the single entry point."""
    from fastapi import APIRouter, Header, HTTPException
    from pydantic import BaseModel
    from {pkg}.platform.layers import assert_can_call
    from . import internal
    from .extensions import DataExt, validators

    router = APIRouter(prefix="/pricing", tags=["domain:pricing"])
    DOMAIN_ID = "business.pricing"

    class QuoteIn(BaseModel):
        plan: str
        age: int
        ext: DataExt | None = None

    class QuoteOut(BaseModel):
        plan: str
        premium: float
        ok: bool
        reasons: list[str]

    @router.post("/quote", response_model=QuoteOut)
    def quote(inp: QuoteIn, x_caller_domain: str = Header(default="product.request-policy")):
        try:
            assert_can_call(x_caller_domain, DOMAIN_ID)
        except PermissionError as e:
            raise HTTPException(403, str(e))
        premium = internal.base_premium(inp.plan, inp.age) * internal.discount_factor(inp.plan)
        reasons = [m for v in validators for m in v(inp.model_dump())]
        return QuoteOut(plan=inp.plan, premium=round(premium, 2), ok=not reasons, reasons=reasons)
    ''', force)
    w(root, f"{pkg}/teams/__init__.py", "", force)
    w(root, f"{pkg}/teams/compliance.py", f'''
    """A team outside the domain: adds logic without touching the gateway (logic extension)."""
    from {pkg}.domains.pricing.extensions import logic_extension

    @logic_extension
    def restricted_list(ctx: dict) -> list[str]:
        ext = ctx.get("ext") or {{}}
        return ["customer on the restricted list"] if ext.get("compliance", {{}}).get("flag") else []
    ''', force)
    w(root, f"{pkg}/main.py", f'''
    from fastapi import FastAPI
    import {pkg}.teams.compliance  # noqa: F401  registers extensions
    from {pkg}.domains.pricing.gateway import router as pricing_gw

    app = FastAPI(title="{pkg} - DOMA")
    app.include_router(pricing_gw)
    ''', force)
    w(root, "tests/test_gateway.py", f'''
    from fastapi.testclient import TestClient
    from {pkg}.main import app

    def test_gateway_and_extension():
        c = TestClient(app)
        ok = c.post("/pricing/quote", json={{"plan": "gold", "age": 30}}).json()
        assert ok["ok"] and ok["premium"] == 27.0
        ko = c.post("/pricing/quote", json={{"plan": "gold", "age": 30, "ext": {{"compliance": {{"flag": True}}}}}}).json()
        assert not ko["ok"]

    def test_layer_rule():
        c = TestClient(app)
        r = c.post("/pricing/quote", json={{"plan": "gold", "age": 30}}, headers={{"x-caller-domain": "infrastructure.storage"}})
        assert r.status_code == 403
    ''', force)
    boundaries = {"kind": "forbidden", "root": pkg, "rules": [
        {"source": f"{pkg}.teams", "forbidden": [f"{pkg}.domains.pricing.internal", f"{pkg}.domains.pricing.gateway"]}]}
    common(root, pkg, "doma-gateway", force, reflex, boundaries)
    w(root, "README.md", f'''
    # {pkg} — DOMA (domain + gateway + layers + extensions)
    - `platform/layers.py` layer design (infrastructure → business → product → presentation → edge).
    - `domains/pricing/gateway.py` the single entry point; `internal.py` invisible outside the domain;
      `extensions.py` extension points (logic: `@logic_extension`; data: the `ext` field).
    - `teams/compliance.py` another team extends the domain without touching the gateway.
    Rule: from outside the domain only the gateway and the extensions are imported/called (see `boundaries.json`).
    ''', force)


GEN = {"layered": layered, "modular-monolith": modular, "hexagonal": hexagonal, "clean": clean,
       "cqrs-es": cqrs, "microkernel": microkernel, "pipes-filters": pipes, "doma-gateway": doma}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pattern", nargs="?", choices=list(PATTERNS))
    ap.add_argument("project", nargs="?", help="Python package name (snake_case)")
    ap.add_argument("--out", default=".", help="target directory (creates <out>/<project>)")
    ap.add_argument("--reflex", action="store_true", help="include the Reflex adapter/UI where it applies")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.pattern:
        for k, v in PATTERNS.items():
            print(f"{k:18} {v}")
        return
    if not a.project or not a.project.isidentifier():
        sys.exit("project must be a valid Python identifier (snake_case)")
    root = Path(a.out) / a.project
    root.mkdir(parents=True, exist_ok=True)
    GEN[a.pattern](root, a.project, a.force, a.reflex)
    print(f"OK {a.pattern} scaffold in {root}")
    for p in sorted(root.rglob("*")):
        if p.is_file():
            print("  ", p.relative_to(root))
    print("\nNext: cd", root, "&& pip install -e '.[dev]' && pytest && uvicorn", f"{a.project}.main:app --reload")


if __name__ == "__main__":
    main()
