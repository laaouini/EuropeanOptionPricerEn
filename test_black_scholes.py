"""Unit tests for the Black-Scholes-Merton European call pricer."""

from __future__ import annotations

import math

import numpy as np
import pytest

from black_scholes import black_scholes_call_price, d1_d2

TOLERANCE = 1e-8

REFERENCE = {
    "spot": 100.0,
    "strike": 100.0,
    "maturity": 1.0,
    "rate": 0.05,
    "volatility": 0.20,
    "dividend_yield": 0.0,
}
REFERENCE_PRICE = 10.450583572185565


def test_reference_example() -> None:
    """Standard textbook example: S0=K=100, T=1, r=5%, sigma=20%, q=0."""
    assert black_scholes_call_price(**REFERENCE) == pytest.approx(REFERENCE_PRICE, abs=TOLERANCE)


def test_dividend_yield_defaults_to_zero() -> None:
    price = black_scholes_call_price(100.0, 100.0, 1.0, 0.05, 0.20)
    assert price == pytest.approx(REFERENCE_PRICE, abs=TOLERANCE)


def test_d1_d2_reference_values() -> None:
    d1, d2 = d1_d2(**REFERENCE)
    assert d1 == pytest.approx(0.35, abs=TOLERANCE)
    assert d2 == pytest.approx(0.15, abs=TOLERANCE)


@pytest.mark.parametrize(
    ("spot", "strike", "maturity", "rate", "volatility", "dividend_yield"),
    [
        (100.0, 100.0, 1.0, 0.05, 0.20, 0.0),
        (50.0, 150.0, 0.25, 0.01, 0.10, 0.0),
        (150.0, 50.0, 2.0, 0.03, 0.40, 0.02),
        (100.0, 120.0, 0.5, -0.01, 0.15, 0.01),
        (100.0, 80.0, 5.0, 0.0, 0.60, 0.04),
    ],
)
def test_price_is_positive(
    spot: float, strike: float, maturity: float, rate: float, volatility: float, dividend_yield: float
) -> None:
    assert black_scholes_call_price(spot, strike, maturity, rate, volatility, dividend_yield) > 0.0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("spot", 0.0),
        ("spot", -100.0),
        ("strike", 0.0),
        ("strike", -1.0),
        ("maturity", 0.0),
        ("maturity", -0.5),
        ("volatility", 0.0),
        ("volatility", -0.2),
        ("spot", math.nan),
        ("strike", math.inf),
        ("maturity", math.nan),
        ("rate", math.nan),
        ("rate", math.inf),
        ("volatility", -math.inf),
        ("dividend_yield", math.nan),
        ("dividend_yield", math.inf),
        ("spot", "abc"),
        ("rate", None),
        ("volatility", True),
    ],
)
def test_invalid_parameters_raise_value_error(field: str, value: object) -> None:
    parameters = dict(REFERENCE)
    parameters[field] = value
    with pytest.raises(ValueError):
        black_scholes_call_price(**parameters)


@pytest.mark.parametrize("rate", [-0.005, -0.01, -0.03])
def test_negative_interest_rate(rate: float) -> None:
    price = black_scholes_call_price(100.0, 100.0, 1.0, rate, 0.20)
    assert math.isfinite(price)
    assert price > 0.0
    # A lower rate must give a lower call price (positive rho).
    assert price < black_scholes_call_price(100.0, 100.0, 1.0, 0.0, 0.20)


def test_negative_interest_rate_matches_closed_form() -> None:
    spot, strike, maturity, rate, volatility = 100.0, 105.0, 0.75, -0.02, 0.25
    vol_sqrt_t = volatility * math.sqrt(maturity)
    d1 = (math.log(spot / strike) + (rate + 0.5 * volatility**2) * maturity) / vol_sqrt_t
    d2 = d1 - vol_sqrt_t
    norm_cdf = lambda x: 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))  # noqa: E731
    expected = spot * norm_cdf(d1) - strike * math.exp(-rate * maturity) * norm_cdf(d2)
    price = black_scholes_call_price(spot, strike, maturity, rate, volatility)
    assert price == pytest.approx(expected, abs=TOLERANCE)


@pytest.mark.parametrize("dividend_yield", [0.01, 0.03, 0.08])
def test_nonzero_dividend_yield_equivalent_to_discounted_spot(dividend_yield: float) -> None:
    """With yield q, the price equals a no-dividend call on S0 * exp(-qT)."""
    spot, strike, maturity, rate, volatility = 100.0, 100.0, 1.0, 0.05, 0.20
    with_dividend = black_scholes_call_price(spot, strike, maturity, rate, volatility, dividend_yield)
    adjusted_spot = spot * math.exp(-dividend_yield * maturity)
    without_dividend = black_scholes_call_price(adjusted_spot, strike, maturity, rate, volatility, 0.0)
    assert with_dividend == pytest.approx(without_dividend, abs=TOLERANCE)


def test_dividend_yield_decreases_call_price() -> None:
    prices = [black_scholes_call_price(100.0, 100.0, 1.0, 0.05, 0.20, q) for q in (0.0, 0.02, 0.05)]
    assert prices[0] > prices[1] > prices[2] > 0.0


def test_negative_dividend_yield_is_accepted() -> None:
    price = black_scholes_call_price(100.0, 100.0, 1.0, 0.05, 0.20, -0.01)
    assert price > REFERENCE_PRICE


@pytest.mark.parametrize(
    ("spot", "strike", "maturity", "rate", "volatility", "dividend_yield"),
    [
        (100.0, 100.0, 1.0, 0.05, 0.20, 0.0),
        (80.0, 100.0, 0.5, 0.02, 0.30, 0.01),
        (120.0, 100.0, 2.0, -0.01, 0.25, 0.03),
        (100.0, 60.0, 3.0, 0.04, 0.10, 0.0),
        (100.0, 140.0, 0.1, 0.0, 0.50, 0.02),
    ],
)
def test_no_arbitrage_bounds(
    spot: float, strike: float, maturity: float, rate: float, volatility: float, dividend_yield: float
) -> None:
    """max(S0 e^{-qT} - K e^{-rT}, 0) <= C <= S0 e^{-qT}."""
    price = black_scholes_call_price(spot, strike, maturity, rate, volatility, dividend_yield)
    discounted_spot = spot * np.exp(-dividend_yield * maturity)
    discounted_strike = strike * np.exp(-rate * maturity)
    lower_bound = max(discounted_spot - discounted_strike, 0.0)
    assert lower_bound - TOLERANCE <= price <= discounted_spot + TOLERANCE


def test_call_price_decreases_with_strike() -> None:
    prices = [black_scholes_call_price(100.0, k, 1.0, 0.05, 0.20) for k in (80.0, 100.0, 120.0)]
    assert prices[0] > prices[1] > prices[2]


def test_call_price_increases_with_volatility() -> None:
    prices = [black_scholes_call_price(100.0, 100.0, 1.0, 0.05, s) for s in (0.10, 0.20, 0.40)]
    assert prices[0] < prices[1] < prices[2]
