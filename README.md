# EuropeanOptionPricerEn

A Python desktop app that prices **European call options** with the analytical **Black-Scholes-Merton** formula. It has a Tkinter GUI.

The pricing logic is kept separate from the user interface, so you can import and unit-test it on its own.

> Scope: European **calls only**. The app does not cover puts, Greeks, Monte Carlo simulation, volatility calibration or other models.

---

## Project Structure

```
EuropeanOptionPricerEn/
├── black_scholes.py        # Pricing engine and input validation
├── main.py                 # Tkinter graphical user interface
├── test_black_scholes.py   # pytest unit tests
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore              # Git exclusions
```

---

## Mathematical Model

The price of a European call on an underlying with a continuous dividend yield is:

$$
C = S_0 \, e^{-qT} \, N(d_1) - K \, e^{-rT} \, N(d_2)
$$

where

$$
d_1 = \frac{\ln(S_0 / K) + \left(r - q + \tfrac{1}{2}\sigma^2\right) T}{\sigma \sqrt{T}},
\qquad
d_2 = d_1 - \sigma \sqrt{T}
$$

and $N(\cdot)$ is the cumulative distribution function of the standard normal distribution. The code uses `scipy.stats.norm.cdf` for it.

Plain-text form:

```
C  = S0 * exp(-q*T) * N(d1) - K * exp(-r*T) * N(d2)
d1 = [ln(S0/K) + (r - q + 0.5*sigma^2) * T] / (sigma * sqrt(T))
d2 = d1 - sigma * sqrt(T)
```

---

## Model Parameters

| Symbol | GUI label                       | Description                                         | Constraint            | Default |
|--------|---------------------------------|-----------------------------------------------------|-----------------------|---------|
| S0     | Underlying Price (S0)           | Current price of the underlying asset               | S0 > 0                | 100     |
| K      | Strike Price (K)                | Exercise price of the option                        | K > 0                 | 100     |
| T      | Time to Maturity (Years)        | Time remaining until expiry, in years               | T > 0                 | 1       |
| r      | Risk-Free Interest Rate (%)     | Continuously compounded annual risk-free rate       | Finite, may be < 0    | 5       |
| sigma  | Volatility (%)                  | Annualised volatility of the underlying's returns   | sigma > 0             | 20      |
| q      | Continuous Dividend Yield (%)   | Continuously compounded annual dividend yield       | Finite, may be < 0    | 0       |

In the GUI, you enter r, sigma and q **as percentages**. They are converted to decimals before pricing (for example, 5 % becomes 0.05). The Python API `black_scholes_call_price` expects **decimal** values.

All inputs must be finite numbers. If an input is empty, non-numeric, infinite, NaN or out of range, the app rejects it and shows an explicit error message.

---

## Installation

Requirements: **Python 3.10+** with Tkinter. The standard Windows installer from python.org includes Tkinter.

```powershell
# Clone the repository
git clone https://github.com/<your-username>/EuropeanOptionPricerEn.git
cd EuropeanOptionPricerEn

# Create and activate a virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

On macOS / Linux, activate the environment with `source .venv/bin/activate`.

> If PowerShell blocks the activation script, run
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.
> You can also skip activation and call `.\.venv\Scripts\python.exe` directly.

---

## Launching the GUI

```powershell
python main.py
```

Without activating the virtual environment:

```powershell
.\.venv\Scripts\python.exe main.py
```

Fill in the six fields, then click **Calculate Call Price** (or press **Enter**). The price is shown with six decimal places.

---

## Example Calculation

| S0  | K   | T | r   | sigma | q  |
|-----|-----|---|-----|-------|----|
| 100 | 100 | 1 | 5 % | 20 %  | 0 % |

- d1 = [ln(1) + (0.05 + 0.5 × 0.04) × 1] / 0.20 = **0.35**
- d2 = 0.35 − 0.20 = **0.15**
- C = 100 × N(0.35) − 100 × e^(−0.05) × N(0.15) = **10.450584**

Using the module directly:

```python
from black_scholes import black_scholes_call_price

price = black_scholes_call_price(
    spot=100, strike=100, maturity=1, rate=0.05, volatility=0.20, dividend_yield=0.0
)
print(f"{price:.6f}")  # 10.450584
```

---

## Running the Unit Tests

```powershell
python -m pytest -v
```

The test suite covers:

- the standard reference example (expected `10.450583572185565`, tolerance `1e-8`) and its d1/d2 values;
- positive prices across a range of parameters;
- invalid parameters: zero or negative S0, K, T or sigma; NaN or infinite values; non-numeric input;
- negative interest rates, checked against an independent closed-form computation;
- non-zero (and negative) dividend yields, using the identity C(S0, q) = C(S0·e^(−qT), 0);
- the no-arbitrage bounds max(S0·e^(−qT) − K·e^(−rT), 0) ≤ C ≤ S0·e^(−qT);
- monotonicity in strike and volatility.

---

## Model Assumptions and Limitations

The Black-Scholes-Merton framework assumes:

- the underlying follows a geometric Brownian motion with **constant volatility**;
- the risk-free rate and the dividend yield are **constant** and continuously compounded;
- markets are frictionless: no transaction costs or taxes, continuous trading, unrestricted short selling and borrowing/lending at the risk-free rate;
- there are no arbitrage opportunities;
- the option is **European**, so it can only be exercised at maturity.

Limitations:

- The model cannot reproduce the volatility smile/skew seen in real markets. Prices depend heavily on the volatility input.
- Dividends are modelled as a continuous yield, not as discrete cash payments.
- The app does not handle American exercise, early exercise premia, jumps, stochastic volatility or stochastic rates.
- Only call options are priced. Puts, Greeks and implied-volatility calibration are deliberately out of scope.
- Use the results for educational and illustrative purposes. They are not trading or investment advice.

---

## License

No license file is included yet. Add one (for example, MIT) before publishing if you want others to be able to reuse the code.
