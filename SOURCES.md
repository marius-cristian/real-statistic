# Master source bibliography

Every number in `data/` is cited at the row level with a `url` and `date_retrieved`. This file groups the URLs by data source for auditing.

## Macroeconomic (data/macro.yaml)

- [Eurostat `nama_10_gdp`](https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nama_10_gdp/A.CP_MEUR.B1GQ.RO+FR+DE+EU27_2020/?startPeriod=2024&endPeriod=2024&format=sdmx-csv): GDP at current market prices, EUR millions, 2024.
- [Eurostat `prc_ppp_ind`](https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_ppp_ind/A.PLI_EU27_2020.GDP.RO+FR+DE+EU27_2020/?startPeriod=2024&endPeriod=2024&format=sdmx-csv): Price Level Index (EU27_2020=100), 2024.
- [Eurostat Statistics Explained: GDP per capita, consumption, price level](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=GDP_per_capita,_consumption_per_capita_and_price_level_indices): the authoritative "EU27=100" GDP/cap PPS headline. RO 77.0, FR 98.2, DE 116.1 (2024 preliminary).
- [Wikipedia: Demographics of the EU](https://en.wikipedia.org/wiki/Demographics_of_the_European_Union): population on 1 Jan 2025, cited from Eurostat `demo_pjan`.
- [ECB daily reference rates](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml): EUR/RON 5.0911 on 2026-04-15.

## Salaries (data/salaries.yaml)

- [Wikipedia: List of European countries by average wage](https://en.wikipedia.org/wiki/List_of_European_countries_by_average_wage): compiled MEAN net monthly wages citing INS Romania, INSEE France, Destatis Germany as upstream sources.
- Direct INS (insse.ro) hit an SSL certificate error at retrieval time. Destatis median bulletin publishes April 2025 gross median 4,784 EUR, distinct from net. INSEE's median-net page returned 404. Medians replace means in a future iteration once direct retrieval succeeds.

## Prices (data/prices/*.yaml)

Every price row lists its retailer URL and date. Grouped by country:

### Romania (data/prices/ro.yaml)
- Real estate: [Storia.ro Bucharest listings](https://www.storia.ro/ro/rezultate/inchiriere/apartament/bucuresti), [SonarHome Bucharest price index](https://sonarhome.ro/preturile-apartamentelor/bucuresti)
- Utilities: [Electrica Furnizare 2026 tariff PDF](https://www.electricafurnizare.ro/app/uploads/2025/12/Oferta-energie-electrica-SU-clienti-casnici-01.01.2026.pdf), [ENGIE residential gas cap](https://www.engie.ro/plafonare/), [Apa Nova Bucuresti](https://www.apanovabucuresti.ro/informatii-utile/tarife-si-facturi/tarife-pentru-consum-apa-si-canalizare)
- Telecom and media: [Digi internet](https://www.digi.ro/servicii/internet/internet-fix), [Digi mobile](https://www.digi.ro/servicii/telefonie-mobila/optim/digi-mobil-optim-nelimitat), [Netflix RO](https://help.netflix.com/en/node/24926), [Spotify RO](https://www.spotify.com/ro-ro/premium/)
- Transport: [STB tarife](https://www.stb.ro/tarife), [Dacia Sandero](https://www.dacia.ro/gama-dacia/sandero/versiuni-si-preturi.html), [PretCarburant OMV](https://pretcarburant.ro/retea/omv), [RCA Bucharest](https://pret-asigurare.ro/rca/bucuresti/)
- Grocery: multiple Carrefour.ro and Bringo product pages
- Leisure: [World Class](https://www.worldclass.ro/abonamente/), [Cinema City RO](https://www.cinemacity.ro/), [Wizz Air OTP-FRA](https://www.wizzair.com/ro-ro/zboruri-ieftine-din-bucuresti-spre-frankfurt-pe-main), [VacanteSmart Antalya](https://www.vacantesmart.ro/)
- Electronics: [Altex iPhone 15](https://altex.ro/), [iSTYLE MacBook Air M3](https://istyle.ro/mac/macbook-air/macbook-air-13-m3.html)

### France (data/prices/fr.yaml)
- Real estate: [SeLoger Paris rent index](https://www.seloger.com/prix-de-l-immo/location/ile-de-france/paris.htm), [MeilleursAgents Paris price](https://www.meilleursagents.com/prix-immobilier/paris-75000/)
- Utilities: [EDF Tarif Bleu](https://particulier.edf.fr/fr/accueil/electricite-gaz/offres-electricite/tarif-bleu.html), [ENGIE gaz](https://particuliers.engie.fr/), [Eau de Paris](https://www.eaudeparis.fr/prix-de-leau)
- Telecom and media: [Sosh fiber](https://shop.sosh.fr/box-internet), [Free Mobile](https://mobile.free.fr/fiche-forfait-free), [Netflix FR](https://help.netflix.com/en/node/24926), [Spotify FR](https://www.spotify.com/fr/premium/)
- Transport: [Ile-de-France Mobilites Navigo 2026](https://www.iledefrance-mobilites.fr/en/tarifs-titre-de-transport-en-commun-2026), [VW Golf FR](https://www.volkswagen.fr/fr/modeles-et-configurateur/golf.html), [prix-carburants.gouv.fr](https://www.prix-carburants.gouv.fr/), [Matmut auto](https://www.matmut.fr/assurance/auto)
- Grocery: multiple Carrefour.fr product pages
- Leisure: [Basic-Fit FR](https://www.basic-fit.com/fr-fr/prix), [UGC Paris tarifs](https://www.allocine.fr/salle/cinema-C0159/tarifs/), [Air France CDG-OTP](https://wwws.airfrance.fr/fr-fr/vols-de-paris-a-bucarest), [Fram Tenerife AI](https://www.fram.fr/)
- Electronics: [Apple FR iPhone 15](https://www.apple.com/fr/shop/buy-iphone/iphone-15), [Apple FR MacBook Air](https://www.apple.com/fr/shop/buy-mac/macbook-air)

### Germany (data/prices/de.yaml)
- Real estate: [ImmoScout24 Berlin Mietspiegel](https://www.immobilienscout24.de/immobilienpreise/berlin/berlin/mietspiegel), [ImmoScout24 Preisatlas](https://atlas.immobilienscout24.de/orte/deutschland/berlin/berlin)
- Utilities: [Verivox Strom](https://www.verivox.de/strom/strompreisentwicklung/), [Verivox Gas](https://www.verivox.de/gas/gaspreisentwicklung/), [Berliner Wasserbetriebe](https://www.bwb.de/de/gebuehren.php)
- Telecom and media: [O2 Home M DSL](https://o2.surfen-telefonieren.de/tarife/festnetz/dsl/o2-home-m-dsl), [Vodafone Tarife](https://www.vodafone.de/privat/handys-tablets-tarife/alle-tarife-mit-vertrag.html), [Netflix DE](https://www.netflix.com/signup?locale=de-DE), [Spotify DE](https://www.spotify.com/de/premium/)
- Transport: [BVG Deutschlandticket](https://www.bvg.de/en/deutschland-ticket), [VW Golf DE](https://www.volkswagen.de/de/modelle/golf.html), [ADAC Spritpreise](https://www.adac.de/news/aktueller-spritpreis/), [HUK24 Vollkasko](https://www.huk24.de/autoversicherung/vollkasko)
- Grocery: multiple REWE.de product pages
- Leisure: [FitX](https://www.fitx.de/mitgliedschaft), [UCI Berlin](https://www.uci-kinowelt.de/kinoinformation/berlin-mercedes-platz/82), [Ryanair BER-OTP](https://www.ryanair.com/flights/de/de/fluege-von-berlin-nach-bukarest), [TUI Mallorca](https://www.tui.com/pauschalreisen/spanien/mallorca/)
- Electronics: [Apple DE iPhone 15](https://www.apple.com/de/shop/buy-iphone/iphone-15/6,1%22-display-128gb-blau), [Apple DE MacBook Air M3](https://www.apple.com/de/shop/buy-mac/macbook-air/13-zoll-m3)

## Retrieval caveats

- All prices retrieved 2026-04-16. Retail prices move. A future run should refresh dates and either re-verify or replace rows.
- A handful of rows (car insurance, some durables where the retailer page did not render the price in WebFetch) are flagged in their `notes` field with the derivation used.
- Several rent and real-estate figures are derived from published per-m&sup2; indices times a standard unit size rather than a live median of listings. Listings pages require JavaScript rendering the WebFetch tool cannot run.
