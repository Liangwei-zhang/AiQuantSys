from us_stock.risk.allocation import calculate_fixed_loss_allocation


def test_fixed_loss_allocation_respects_loss_amount() -> None:
    result = calculate_fixed_loss_allocation(
        account_equity=100_000,
        entry_price=100,
        stop_price=95,
        loss_pct=0.01,
    )

    assert result.shares == 200
    assert result.notional == 20_000
    assert result.max_allowed_loss == 1_000
    assert result.loss_per_share == 5


def test_fixed_loss_allocation_respects_max_allocation() -> None:
    result = calculate_fixed_loss_allocation(
        account_equity=100_000,
        entry_price=100,
        stop_price=99,
        loss_pct=0.01,
        max_allocation_pct=0.1,
    )

    assert result.shares == 100
    assert result.notional == 10_000
