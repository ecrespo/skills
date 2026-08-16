# Python / FastAPI / Reflex code shapes per architecture

Minimal, illustrative code showing the *shape* of each architecture. Not production code:
add error handling, config, typing and tests. Domain names use an insurance example
(policy, payment, beneficiary); rename to the user's domain.

Contents: 1 Layered - 2 Modular Monolith - 3 Client-Server - 4 Microservices - 5 SOA -
6 EDA - 7 Serverless - 8 Hexagonal - 9 Clean - 10 CQRS+ES - 11 Microkernel - 12 Pipes&Filters -
13 Space-Based - 14 Service-Based - 15 Micro-frontends - 16 P2P - 17 Cell-Based - 18 Agentic -
19 DOMA

## 1. Layered
```python
# app/main.py - presentation
from fastapi import FastAPI, Depends
app = FastAPI()
def get_service(): return PolicyService(PolicyRepoMongo())
@app.get("/policies/{number}")
def get_policy(number: str, svc: "PolicyService" = Depends(get_service)): return svc.get(number)

# app/services.py - service
class PolicyService:
    def __init__(self, repo): self.repo = repo
    def get(self, number: str) -> dict:
        p = self.repo.find_by_number(number)
        if p is None: raise ValueError("policy not found")
        return {"policy_number": p["policy_number"], "status": p["status"]}

# app/repositories.py - persistence
class PolicyRepoMongo:
    def __init__(self):
        from pymongo import MongoClient
        self.col = MongoClient()["db"]["policies"]
    def find_by_number(self, number): return self.col.find_one({"policy_number": number})

# Reflex in the same process
import reflex as rx
class PolicyState(rx.State):
    number: str = ""; result: str = ""
    def search(self): self.result = str(PolicyService(PolicyRepoMongo()).get(self.number))
```

## 2. Modular monolith
```python
# project/{policies,payments}/{api.py,domain.py,repo.py}  shared/events.py  main.py
# shared/events.py - in-process bus
from collections import defaultdict
_subs = defaultdict(list)
def subscribe(event, handler): _subs[event].append(handler)
def publish(event, payload):
    for h in _subs[event]: h(payload)

# payments/api.py - the module's only public surface
from fastapi import APIRouter
from shared.events import publish
router = APIRouter(prefix="/payments")
@router.post("/confirm/{ref}")
def confirm(ref: str):
    publish("PaymentConfirmed", {"ref": ref, "policy_number": "P-100"}); return {"ok": True}

# policies/api.py - subscribes; never imports payments.repo or payments.domain
from shared.events import subscribe
subscribe("PaymentConfirmed", lambda p: print(f"Activating {p['policy_number']}"))
```
```ini
# .importlinter
[importlinter]
root_package = project
[importlinter:contract:independent-modules]
name = Modules do not import other modules' internals
type = independence
modules =
    project.policies
    project.payments
```

## 3. Client-server (FastAPI server + Reflex client)
```python
# server: FastAPI
@app.get("/api/beneficiaries/{document_id}")
def beneficiary(document_id: str): return {"document_id": document_id, "status": "ACTIVE"}
# client: Reflex
class State(rx.State):
    document_id: str = ""; data: dict = {}
    async def query(self):
        async with httpx.AsyncClient() as c:
            self.data = (await c.get(f"http://api/api/beneficiaries/{self.document_id}")).json()
```

## 4. Microservices (choreographed saga + circuit breaker)
```python
# payment_service: publishes an event (simplified outbox)
r.xadd("events.payments", {"type": "PaymentConfirmed", "data": json.dumps({"ref": ref, "policy_number": number})})

# policy_service/worker: idempotent consumer
for msg_id, fields in msgs:
    if msg_id in processed: continue
    if fields[b"type"] == b"PaymentConfirmed": activate_policy(json.loads(fields[b"data"])["policy_number"])
    processed.add(msg_id)

# minimal circuit breaker on an outbound call
if time.time() < _open_until: raise HTTPException(503, "circuit open")
try:
    resp = await c.get(url, timeout=1.5); _failures = 0
except httpx.HTTPError:
    _failures += 1
    if _failures >= 3: _open_until = time.time() + 30
    raise HTTPException(502)
```

## 5. SOA (integration service, canonical model)
```python
class CanonicalCustomer(BaseModel): id: str; name: str; document: str; source: str
def _from_core(raw): return CanonicalCustomer(id=raw["CLI_ID"], name=raw["FULL_NAME"], document=raw["DOC_ID"], source="core")
def _from_crm(raw):  return CanonicalCustomer(id=raw["uuid"], name=raw["fullName"], document=raw["docNumber"], source="crm")
@app.get("/canonical/customer/{doc}", response_model=CanonicalCustomer)
async def customer(doc: str):
    core = await c.get(f"http://core/customer/{doc}")
    return _from_core(core.json()) if core.status_code == 200 else _from_crm((await c.get(f"http://crm/contacts?doc={doc}")).json()[0])
```

## 6. EDA (aio-pika, outbox, DLQ, idempotency)
```python
# producer
event = {"id": f"evt-{ref}", "type": "payments.PaymentConfirmed", "source": "payment-service",
         "time": datetime.now(timezone.utc).isoformat(), "data": {"ref": ref, "policy_number": number}}
ex = await ch.declare_exchange("domain", aio_pika.ExchangeType.TOPIC, durable=True)
await ex.publish(aio_pika.Message(json.dumps(event).encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT), routing_key=event["type"])
# consumer
q = await ch.declare_queue("policy-activator", durable=True, arguments={"x-dead-letter-exchange": "dlx"})
await q.bind(ex, routing_key="payments.*")
async for msg in q.iterator():
    async with msg.process(requeue=False):
        ev = json.loads(msg.body)
        if already_processed(ev["id"]): continue
        activate_policy(ev["data"]["policy_number"]); mark_processed(ev["id"])
```

## 7. Serverless
```python
# HTTP API
from mangum import Mangum
handler = Mangum(app)
# one function per storage event
def handler(event, context):
    for rec in event["Records"]:
        text = run_ocr(rec["s3"]["bucket"]["name"], rec["s3"]["object"]["key"])
        publish_to_queue({"text": text})
```
```yaml
functions:
  api: { handler: lambda_api/handler.handler, events: [{ httpApi: { path: /{proxy+}, method: any } }] }
  ocr: { handler: lambda_ocr/handler.handler, timeout: 120, events: [{ s3: { bucket: invoices, event: "s3:ObjectCreated:*" } }] }
```

## 8. Hexagonal
```python
# core/domain.py - no frameworks
@dataclass
class Policy:
    policy_number: str; status: Status = Status.PENDING; events: list = field(default_factory=list)
    def activate(self):
        if self.status is Status.ACTIVE: raise ValueError("already active")
        self.status = Status.ACTIVE; self.events.append({"type": "PolicyActivated", "number": self.policy_number})
# core/ports.py
class PolicyRepository(Protocol):
    def get(self, number: str) -> Policy | None: ...
    def save(self, p: Policy) -> None: ...
class EventPublisher(Protocol):
    def publish(self, e: dict) -> None: ...
# core/use_cases.py - input port
class ActivatePolicy:
    def __init__(self, repo: PolicyRepository, publisher: EventPublisher): self.repo, self.publisher = repo, publisher
    def __call__(self, number: str) -> Policy:
        p = self.repo.get(number)
        if p is None: raise LookupError("not found")
        p.activate(); self.repo.save(p)
        for e in p.events: self.publisher.publish(e)
        return p
# adapters/persistence: MongoPolicyRepo, InMemoryPolicyRepo (tests)
# adapters/api/fastapi_app.py
def build_app(activate: ActivatePolicy) -> FastAPI:
    app = FastAPI()
    @app.post("/policies/{number}/activate")
    def ep(number: str):
        try: return {"status": activate(number).status}
        except LookupError as e: raise HTTPException(404, str(e))
        except ValueError as e: raise HTTPException(409, str(e))
    return app
# adapters/ui/reflex_app.py - same use case, driven from Reflex
class State(rx.State):
    number: str = ""; msg: str = ""
    def activate(self): self.msg = str(activate_uc(self.number).status)
# main.py - composition root
activate_uc = ActivatePolicy(MongoPolicyRepo(uri), RabbitPublisher()); app = build_app(activate_uc)
# tests - no infrastructure
def test_activate():
    repo = InMemoryPolicyRepo(); repo.save(Policy("P-1")); pub = []
    uc = ActivatePolicy(repo, type("P", (), {"publish": lambda s, e: pub.append(e)})())
    assert uc("P-1").status is Status.ACTIVE and pub[0]["type"] == "PolicyActivated"
```

## 9. Clean
```text
src/
├── domain/entities/policy.py                 # no dependencies
├── application/{ports,dto,use_cases}/        # ActivatePolicyUseCase.execute(Input) -> Output
├── interface_adapters/{controllers,presenters,repositories}/
└── infrastructure/{web/routers,db,di.py}
```
```python
@dataclass(frozen=True)
class ActivatePolicyInput: policy_number: str; user: str
class ActivatePolicyUseCase:
    def __init__(self, repo, uow): self.repo, self.uow = repo, uow
    def execute(self, inp: ActivatePolicyInput) -> ActivatePolicyOutput:
        with self.uow:
            p = self.repo.get(inp.policy_number); p.activate(by=inp.user); self.repo.save(p); self.uow.commit()
        return ActivatePolicyOutput(p.policy_number, p.status.value)
# router -> controller (Pydantic response) -> use case -> repo
```

## 10. CQRS + Event Sourcing
```python
class PolicyAggregate:
    def __init__(self, number): self.number, self.status, self.version, self._new = number, "PENDING", 0, []
    def activate(self):                                  # decide
        if self.status == "ACTIVE": raise ValueError("already active")
        self._emit("PolicyActivated", {"number": self.number})
    def _apply(self, e):                                 # evolve
        if e.type == "PolicyActivated": self.status = "ACTIVE"
        self.version = e.version
    def _emit(self, type_, data):
        e = Event(type_, data, self.version + 1); self._apply(e); self._new.append(e)
    @classmethod
    def from_history(cls, number, history):
        a = cls(number); [a._apply(e) for e in history]; return a
# store: unique index (stream, version) = optimistic concurrency
col.create_index([("stream", 1), ("version", 1)], unique=True)
# API: /commands/... writes (aggregate + store + projection); /queries/... reads the read model only
```

## 11. Microkernel
```python
@runtime_checkable
class ValidatorPlugin(Protocol):
    name: str; priority: int
    def validate(self, invoice: dict) -> list[str]: ...
class Kernel:
    def __init__(self):
        self.plugins = sorted((ep.load()() for ep in entry_points(group="invoices.validators")), key=lambda p: p.priority)
    def run(self, invoice):
        errors = {p.name: e for p in self.plugins if (e := p.validate(invoice))}
        return {"valid": not errors, "errors": errors}
# plugin pyproject: [project.entry-points."invoices.validators"] arithmetic = "plugins.arithmetic:ArithmeticValidator"
```

## 12. Pipes & Filters
```python
def ocr(pages: Iterable[bytes]) -> Iterable[Line]: ...
def extract_items(lines: Iterable[Line]) -> Iterable[Item]: ...
def validate(items: Iterable[Item]) -> Iterable[Item]: ...
def enrich(items: Iterable[Item], catalog) -> Iterable[dict]: ...
pipeline = lambda pages, cat: list(enrich(validate(extract_items(ocr(pages))), cat))
# streaming in FastAPI: async generators + StreamingResponse(a_json(a_items(a_ocr(data))), media_type="application/x-ndjson")
```

## 13. Space-Based
```python
if not await grid.hsetnx(f"seats:{event}", seat, user): raise HTTPException(409)   # atomic in the grid
await grid.xadd("data_pump", {"op": "reserve", "data": json.dumps({...})})         # write-behind
# data_writer: xread count=500 -> persist_batch_in_mongo(batch)
```

## 14. Service-Based
```python
OWNERSHIP = {"policies": "underwriting", "payments": "billing"}
def assert_owner(service, collection, write):
    if write and OWNERSHIP[collection] != service: raise PermissionError(f"{service} cannot write to {collection}")
# cross-service reads allowed; writes only through the owner's API/events
```

## 15. Micro-frontends (Reflex by route)
```python
# mf_policies: rx.App().add_page(index, route="/policies")   # :3001
# mf_payments: rx.App().add_page(index, route="/payments")   # :3002
```
```nginx
location /policies { proxy_pass http://mf-policies:3001; }
location /payments { proxy_pass http://mf-payments:3002; }
location /         { proxy_pass http://shell:3000; }
```

## 16. P2P (asyncio gossip)
```python
async def handle(self, reader, writer):
    msg = json.loads(await reader.readline()); writer.close()
    if msg["id"] in self.seen: return
    self.seen.add(msg["id"]); await self.gossip(msg)
```

## 17. Cell-Based (router)
```python
def cell_for(tenant):
    if tenant in PINNED: return CELLS[PINNED[tenant]]
    return list(CELLS.values())[int(hashlib.sha256(tenant.encode()).hexdigest(), 16) % len(CELLS)]
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path, request: Request): ...  # httpx towards cell_for(request.headers["x-tenant-id"])
```

## 18. Agentic (LangGraph)
```python
g = StateGraph(State)
g.add_node("router", router); g.add_node("payments", payments_agent); g.add_node("policies", policies_agent)
g.add_edge(START, "router"); g.add_conditional_edges("router", decide); g.add_edge("payments", END); g.add_edge("policies", END)
graph = g.compile()
@app.post("/ask")
async def ask(question: str): return await graph.ainvoke({"question": question, "route": "", "answer": ""})
```

## 19. DOMA
```python
# domains/pricing/gateway.py - single entry point
@app.post("/quote", response_model=QuoteOut)
async def quote(inp: QuoteIn, caller: str = Depends(get_caller)):
    assert_can_call(caller, "business.pricing")                     # layer design
    base = (await c.get(f"http://svc-quoting/base/{inp.plan}")).json()["premium"]   # internals stay invisible
    reasons = [m for v in validators for m in v(inp.model_dump())]  # logic extensions
    return QuoteOut(premium=base, ok=not reasons, reasons=reasons)
# platform/layers.py
LAYERS = ["infrastructure", "business", "product", "presentation", "edge"]
def assert_can_call(caller, callee):
    if LAYERS.index(caller.split(".")[0]) <= LAYERS.index(callee.split(".")[0]) and caller.split(".")[0] != callee.split(".")[0]:
        raise PermissionError("violates layer design")
# domains/pricing/extensions.py
DataExt = dict[str, Any]; validators: list[Callable[[dict], list[str]]] = []
def logic_extension(fn): validators.append(fn); return fn
# teams/compliance/ext_pricing.py - another team, without touching the gateway
@logic_extension
def sanctioned(ctx): return ["restricted list"] if (ctx.get("ext") or {}).get("compliance", {}).get("flag") else []
```
```ini
[importlinter:contract:doma-layers]
name = Layers only depend downwards
type = layers
layers =
    edge
    presentation
    product
    business
    infrastructure
containers = domains
```
