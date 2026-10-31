"""Analytical Black-Scholes-Merton pricing for European call options.

This module is independent of any user interface so that the pricing logic
can be imported, reused and unit tested on its own.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import norm


def _require_finite(name: str, value: float) -> float:
    """Return ``value`` as a float, raising ``ValueError`` if it is not a finite real number."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a real number, not a boolean.")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a real number.") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number.")
    return number


def _require_positive(name: str, value: float) -> float:
    """Return ``value`` as a float, raising ``ValueError`` unless it is finite and strictly positive."""
    number = _require_finite(name, value)
    if number <= 0.0:
        raise ValueError(f"{name} must be strictly positive.")
    return number


def validate_parameters(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
) -> tuple[float, float, float, float, float, float]:
    """Validate Black-Scholes inputs and return them as floats.

    Args:
        spot: Current underlying price S0 (must be > 0).
        strike: Strike price K (must be > 0).
        maturity: Time to maturity T in years (must be > 0).
        rate: Continuously compounded risk-free rate r, in decimal form (may be negative).
        volatility: Annualised volatility sigma, in decimal form (must be > 0).
        dividend_yield: Continuous dividend yield q, in decimal form (may be negative).

    Returns:
        The validated parameters ``(spot, strike, maturity, rate, volatility, dividend_yield)``.

    Raises:
        ValueError: If any parameter is non-numeric, non-finite or out of range.
    """
    return (
        _require_positive("Underlying price (S0)", spot),
        _require_positive("Strike price (K)", strike),
        _require_positive("Time to maturity (T)", maturity),
        _require_finite("Risk-free interest rate (r)", rate),
        _require_positive("Volatility (sigma)", volatility),
        _require_finite("Dividend yield (q)", dividend_yield),
    )


def d1_d2(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
) -> tuple[float, float]:
    """Compute the Black-Scholes-Merton ``d1`` and ``d2`` terms.

    d1 = [ln(S0/K) + (r - q + 0.5 * sigma^2) * T] / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    Inputs are validated with :func:`validate_parameters`.
    """
    spot, strike, maturity, rate, volatility, dividend_yield = validate_parameters(
        spot, strike, maturity, rate, volatility, dividend_yield
    )
    vol_sqrt_t = volatility * np.sqrt(maturity)
    d1 = (
        np.log(spot / strike) + (rate - dividend_yield + 0.5 * volatility**2) * maturity
    ) / vol_sqrt_t
    d2 = d1 - vol_sqrt_t
    return float(d1), float(d2)


def black_scholes_call_price(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
) -> float:
    """Price a European call option with the Black-Scholes-Merton formula.

    C = S0 * exp(-q * T) * N(d1) - K * exp(-r * T) * N(d2)

    Args:
        spot: Current underlying price S0 (must be > 0).
        strike: Strike price K (must be > 0).
        maturity: Time to maturity T in years (must be > 0).
        rate: Continuously compounded risk-free rate r, in decimal form (e.g. 0.05 for 5%).
        volatility: Annualised volatility sigma, in decimal form (e.g. 0.20 for 20%).
        dividend_yield: Continuous dividend yield q, in decimal form (default 0.0).

    Returns:
        The theoretical European call price.

    Raises:
        ValueError: If any parameter is invalid.

    Example:
        >>> round(black_scholes_call_price(100, 100, 1, 0.05, 0.20), 6)
        10.450584
    """
    spot, strike, maturity, rate, volatility, dividend_yield = validate_parameters(
        spot, strike, maturity, rate, volatility, dividend_yield
    )
    d1, d2 = d1_d2(spot, strike, maturity, rate, volatility, dividend_yield)
    discounted_spot = spot * np.exp(-dividend_yield * maturity)
    discounted_strike = strike * np.exp(-rate * maturity)
    price = discounted_spot * norm.cdf(d1) - discounted_strike * norm.cdf(d2)
    return float(price)
