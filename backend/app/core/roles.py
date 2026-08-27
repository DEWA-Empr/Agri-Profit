"""Who may do what, in one table.

WHY THERE ARE THREE ROLES AND NOT TEN. The PRD names ten personas — farm worker,
farm manager, crop processing manager, farm operator, farm owner, financial
officer, financial planner, equipment manager, bank loan officer, private
investor. Most of those differ in what a person *does*, not in what the system
must *stop them doing*, and a role that grants exactly what another role grants
is documentation wearing a permission's clothes. Collapsing them to the
boundaries the platform can actually enforce leaves three, each justified by a
real consequence:

  OWNER    everything, plus minting share links and managing members. Handing an
           outsider a link to the farm's finances is an ownership decision, and
           so is deciding who else may log in.
  MANAGER  full operational and financial control of the farm. Cannot share the
           farm's position outside it, and cannot add users.
  WORKER   field entry. Records activity and reads the farm's own log, but does
           not see the aggregate financial picture, cannot reverse an entry
           (a reversal edits financial history), and cannot touch equipment,
           whose depreciation rate silently moves every break-even price.

THE TWO EXTERNAL PERSONAS ARE DELIBERATELY NOT ROLES. A bank loan officer and a
private investor already have a mechanism — the tokenised, revocable, expiring
share link, which grants read-only access to one farm's report with no account
at all. Modelling them as roles would mean issuing them credentials to a system
they have no other reason to enter, and would leave two ways to answer the same
question. The share link is the narrower capability and it already works.

THE TABLE IS THE POLICY. `ROLE_PERMISSIONS` is the single place a grant is
written down. Endpoints ask for a permission, never for a role, so widening what
a manager may do is one edit here rather than a search through the route layer
for `role == "manager"`. `test_authorization.py` asserts the table's shape
directly, so a grant cannot be widened by accident.
"""
from enum import Enum


class Role(str, Enum):
    """Stored as a plain string, not a database enum type.

    A native Postgres ENUM would need a migration to add a value, and roles are
    the thing most likely to gain one. `str` mixin so a role compares equal to
    its stored value and serialises without a custom encoder.
    """
    OWNER = "owner"
    MANAGER = "manager"
    WORKER = "worker"


class Permission(str, Enum):
    """A single thing a caller may attempt.

    Named for the business operation rather than the route, so that moving or
    splitting an endpoint does not require renaming a permission.
    """
    # Operational records
    LOG_CREATE = "log:create"        # post an operational log (and its paired transaction)
    LOG_READ = "log:read"            # read the farm's own operational records
    LOG_REVERSE = "log:reverse"      # post a contra entry — edits financial history

    # Money
    FINANCE_READ = "finance:read"    # P&L, transactions, summary, DSS, enterprise economics

    # Machinery
    EQUIPMENT_READ = "equipment:read"
    EQUIPMENT_MANAGE = "equipment:manage"   # create/correct equipment and maintenance

    # Tier-2 forecast
    FORECAST_READ = "forecast:read"  # model metadata; the entry form reads this
    FORECAST_USE = "forecast:use"    # request a yield prediction

    # Disclosure and identity
    SHARE_MANAGE = "share:manage"    # mint, list and revoke investor links
    MEMBER_MANAGE = "member:manage"  # add users to the farm, change their role

    # Operator-only. Retraining rewrites the ONE model artefact every farm's
    # predictions are served from, so it is a cross-tenant side effect and is
    # granted to no role at all — see ROLE_PERMISSIONS and
    # Settings.allow_api_model_training.
    MODEL_TRAIN = "model:train"


_WORKER_PERMISSIONS = frozenset({
    Permission.LOG_CREATE,
    Permission.LOG_READ,
    # The entry form reads the model's crop list to build its selector, so a
    # worker who cannot read this cannot file a record at all.
    Permission.FORECAST_READ,
})

_MANAGER_PERMISSIONS = _WORKER_PERMISSIONS | {
    Permission.LOG_REVERSE,
    Permission.FINANCE_READ,
    Permission.EQUIPMENT_READ,
    Permission.EQUIPMENT_MANAGE,
    Permission.FORECAST_USE,
}

_OWNER_PERMISSIONS = _MANAGER_PERMISSIONS | {
    Permission.SHARE_MANAGE,
    Permission.MEMBER_MANAGE,
}

ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.WORKER: frozenset(_WORKER_PERMISSIONS),
    Role.MANAGER: frozenset(_MANAGER_PERMISSIONS),
    Role.OWNER: frozenset(_OWNER_PERMISSIONS),
}

# The role every account gets when a farm is created, and the role every account
# that predates roles was backfilled to (migration a8d4e1c60b27). Registration
# creates the farm, so the registrant owns it.
DEFAULT_ROLE = Role.OWNER


def permissions_for(role: Role | str) -> frozenset[Permission]:
    """What `role` may do. An unrecognised role gets nothing.

    Failing closed matters here: a row carrying a role this build does not know
    about — a downgrade after a new role shipped, or a hand-edited database —
    must lose access rather than gain it.
    """
    try:
        return ROLE_PERMISSIONS[Role(role)]
    except (ValueError, KeyError):
        return frozenset()


def has_permission(role: Role | str, permission: Permission) -> bool:
    return permission in permissions_for(role)
