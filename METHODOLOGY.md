# Methodology

This document defines the theory the pipeline implements. Formulas live here first. The code in `src/real_statistic/compute.py` must match them exactly.

## Step 0. Notation

- `C = {RO, FR, DE}` are the target countries, plus `EU27` for Eurostat-baseline comparisons.
- `B = {survival, middle_class, global, housing_only}` are the basket types.
- `I_b` is the canonical item list for basket `b` (see `data/baskets.yaml`).
- `q[i, b]` is the monthly quantity of item `i` in basket `b`.
- `p[i, c]` is the price of item `i` in country `c` at a local retailer, in that country's local currency.
- `fx[c -> EUR]` is the exchange rate converting country `c`'s local currency into EUR.
- `net[c]` is the median net monthly salary in country `c`, local currency.

## Step 1. Reproduce the official Eurostat PPS figure

This step proves we understand the methodology we are critiquing. If we cannot reproduce Eurostat's own numbers from their raw inputs, every downstream claim is suspect.

Eurostat defines GDP per capita in PPS as:

```
GDP_PPS_per_capita[c] = GDP_nominal_EUR[c] / population[c] / PPP[c]
official_index[c]     = 100 * GDP_PPS_per_capita[c] / GDP_PPS_per_capita[EU27]
```

`PPP[c]` is Eurostat's published purchasing power parity (units of local currency per EUR of real purchasing power; for euro-zone countries it reflects only the price level deviation).

**Validation gate.** Our `official_index[c]` must match Eurostat's published index within +/- 1 percentage point, using the same reference year. If not, fix the bug before proceeding.

## Step 2. Basket cost in local currency

For each basket `b` and pricing country `pc`:

```
basket_cost_local[b, pc] = sum over i in I_b of p[i, pc] * q[i, b]
```

Units: local currency (RON for RO, EUR for FR and DE). Quantities are monthly. Durables (laptop, phone, car) use a fixed amortization period documented in `baskets.yaml`.

## Step 3. Convert to EUR

```
basket_cost_eur[b, pc] = basket_cost_local[b, pc] * fx[pc -> EUR]
net_eur[c]             = net[c] * fx[c -> EUR]
```

FX rates come from the ECB reference rate on a fixed retrieval date (committed in `data/macro.yaml`). For EUR-denominated countries `fx[c -> EUR] = 1`.

## Step 4. Baskets per month (the core metric)

```
bpm[b, sc, pc] = net_eur[sc] / basket_cost_eur[b, pc]
```

This is the number of full copies of basket `b`, priced at `pc`'s retailers, that country `sc`'s median net salary buys in one month. The full 4 * 3 * 3 = 36-cell cube is the answer sheet.

- `bpm[middle_class, DE, DE]` is the baseline domestic German experience.
- `bpm[middle_class, RO, RO]` is Romanian on Romanian prices for a Romanian middle-class basket. What the PPS number roughly tracks.
- `bpm[middle_class, RO, FR]` is a Romanian trying to live the French middle-class life at French prices. This is where the illusion collapses.
- `bpm[survival, FR, RO]` is a French person buying a Romanian survival basket. This is where Romania is genuinely cheaper.

## Step 5. Relative purchasing power index (anchored on DE/DE)

```
RPP[b, sc, pc] = 100 * bpm[b, sc, pc] / bpm[middle_class, DE, DE]
```

Germany on German prices at `middle_class` equals 100 by construction. Everything else is scaled relative to that.

## Step 6. PPS divergence

This is the money shot. It measures how much Eurostat's headline PPS number deviates from real per-basket purchasing power.

```
rescaled[b, c]  = bpm[b, c, c] / bpm[b, DE, DE] * official_index[DE]
divergence[b, c] = official_index[c] - rescaled[b, c]
```

By construction `divergence[b, DE] = 0`. Positive values mean PPS flatters country `c` for basket `b`. Negative values mean PPS understates.

Expected shape if the thesis holds:
- `survival` basket: divergence near zero. Eurostat's weights skew domestic, so PPS roughly matches a cheap local basket.
- `middle_class` basket: small positive divergence for RO.
- `global` basket: large positive divergence for RO. Tradables don't PPP-adjust.
- `housing_only`: direction depends on capital-vs-rural and varies by country.

## Step 7. Cross-country purchasing power index

Answers "how far behind is RO on a DE basket" and "how far ahead are DE/FR on a RO basket":

```
cross_index[b, sc, pc] = 100 * bpm[b, sc, pc] / bpm[b, pc, pc]
```

Reads as: "country `sc`'s median net salary buys X% of the basket that country `pc`'s median net salary buys, at `pc`'s own prices." Examples:

- `cross_index[middle_class, RO, FR] = 30`. A Romanian on the RO median net has 30% of the middle-class purchasing power a French person has in France.
- `cross_index[survival, DE, RO] = 450`. A German on the DE median net affords 4.5 times the Romanian survival basket a Romanian affords in Romania.

## Step 8. Sanity checks

The pipeline checks that:
1. Every item in `baskets.yaml` has a price entry in each of `data/prices/{ro,fr,de}.yaml`.
2. Every price row has `url`, `date_retrieved`, `unit`, `price`, `currency`.
3. FX rates in `macro.yaml` are dated within 60 days of the median price retrieval date.
4. The reproduced PPS index matches Eurostat's official index within +/- 1 pp for RO, FR, DE.

Violations abort the build with a specific error. No partial builds.

## Assumptions and honest limitations

- **Median, not mean.** Median net monthly salary is the pipeline input. Mean is reported alongside for reference but never used in core metrics.
- **National-level only.** No urban-rural or capital-secondary split. Bucharest vs rural Romania is a real gap this project does not address.
- **Listed rent, not signed rent.** Rent figures come from a major listings portal, not actual lease contracts. Listed rents skew high.
- **Linear amortization for durables.** Ignores financing cost and actual replacement behavior.
- **Taxes already netted.** Using published net salaries dodges the income-tax regime question. VAT is embedded in retail prices.
- **No child or family benefits, no regional subsidies.** Single-earner household comparison.
- **FX at a point in time.** No trailing-average smoothing. EUR/RON has been near-stable; EUR/EUR is 1.

### Capital-density premium

All rent and real-estate lines use capital-city prices: Bucharest, Paris, Berlin. This is not a neutral choice. Paris is a globally unique city: a top tourist destination, financial hub, government seat, and cultural capital with severe supply constraints inside the p&eacute;riph&eacute;rique. Its per-m&sup2; rent and purchase prices carry a global-city premium that has little to do with what the typical French salary earner pays for housing. Berlin is noticeably cheaper than Munich, Frankfurt, or Hamburg. Bucharest is close to the Romanian national rent average because Romania has no other comparably large city.

Concretely: SeLoger Paris rent runs about 25 EUR/m&sup2;/month against an INSEE national average of roughly 11 to 12 EUR/m&sup2;/month. The capital is roughly double the country. Berlin is closer to Germany's urban average, and Bucharest carries a small premium (about 20 to 30%) over Romania's national rent.

**Implication.** Capital-to-capital overstates Romania's housing disadvantage, because Paris rents reflect Paris density more than French purchasing power. A fair national-vs-national comparison would narrow the housing gap somewhat. It would not narrow the tradables gap (iPhones, laptops, flights cost the same in Paris and rural France).

The `global` basket matters precisely because it is immune to the capital-density artifact. If RO still looks far behind on the `global` basket, where rents do not enter at all, then the PPS overstatement is real and not an artifact of capital choice.

A future iteration could add a national-median rent series per country alongside the capital figure.

### Amenity value that baskets cannot price

A basket of goods and services counts what the shopper pays. It cannot count what the shopper gets beyond the transaction. Paris does not just charge a lot for rent. It delivers world-class museums, gastronomy, architecture, nightlife, concerts, and cultural density that a Parisian salary earner consumes as a matter of daily life. A lot of that is free or nearly free at the point of use: the Seine, the parks, the buskers, the window shopping, neighborhood bakeries. Berlin has a different but equally rich cultural-amenity profile. Bucharest has a growing scene but a fraction of the density.

The basket method treats this as pure cost. "Paris housing is 3x more expensive" without recognizing that part of that price is proximity to amenities that are genuinely valuable. Economists call this consumer surplus from location. It is a real welfare good that neither PPS nor this project's basket methodology can measure.

The same point cuts across everything amenity-like: luxury retail (Herm&egrave;s flagship, the Galeries Lafayette corridor, boutiques only a handful of cities have), fashion weeks, film festivals, Michelin-starred density, trade fairs, easy day-trips to other world-class cities, depth and specialization of the job market. Berlin has its own version (underground music, galleries, a tech scene; less luxury, more raw cultural density). Bucharest has its version (growing, thinner, less deep). This asymmetry is real, it runs in one direction, and our numbers cannot see it.

It cuts symmetrically. Every capital has amenity value our baskets do not count. Paris has more than Berlin, Berlin has more than Bucharest, but each has something. So the honest framing is not "Paris is undervalued, Bucharest is overvalued." It is "amenities are not in the frame at all, and readers should remember that when they look at the numbers."

The honest take:

- For a pure "how many physical units of X does my salary buy" comparison, use this project's basket method.
- For a "how much wellbeing does my salary buy" comparison, neither basket methods nor PPS answer that.
- Both PPS and this project agree on one thing: tradable goods (iPhones, laptops, flights) are a clean comparator. They do not carry location premia and they do not carry amenity surplus. They just cost money.

The `global` basket carries most of the argumentative weight precisely because it sidesteps both the capital-density premium and the amenity-value confound.
