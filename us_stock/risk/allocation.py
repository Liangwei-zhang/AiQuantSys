from pydantic import BaseModel


class AllocationSizeResult(BaseModel):
    shares: int
    notional: float
    max_allowed_loss: float
    loss_per_share: float


class AllocationSizingError(ValueError):
    pass


def calculate_fixed_loss_allocation(
    account_equity: float,
    entry_price: float,
    stop_price: float,
    loss_pct: float,
    max_allocation_pct: float | None = None,
) -> AllocationSizeResult:
    """Calculate share quantity from account size, entry price and stop price."""

    if account_equity <= 0:
        raise AllocationSizingError("account_equity_must_be_positive")
    if entry_price <= 0 or stop_price <= 0:
        raise AllocationSizingError("prices_must_be_positive")
    if not 0 < loss_pct <= 1:
        raise AllocationSizingError("loss_pct_must_be_between_0_and_1")

    loss_per_share = abs(entry_price - stop_price)
    if loss_per_share <= 0:
        raise AllocationSizingError("loss_per_share_must_be_positive")

    max_allowed_loss = account_equity * loss_pct
    shares = int(max_allowed_loss / loss_per_share)

    if max_allocation_pct is not None:
        if not 0 < max_allocation_pct <= 1:
            raise AllocationSizingError("max_allocation_pct_must_be_between_0_and_1")
        max_notional = account_equity * max_allocation_pct
        shares = min(shares, int(max_notional / entry_price))

    notional = shares * entry_price
    return AllocationSizeResult(
        shares=shares,
        notional=notional,
        max_allowed_loss=max_allowed_loss,
        loss_per_share=loss_per_share,
    )
