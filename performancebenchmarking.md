**AGRI-PROFIT --- Performance Benchmarking**

Evaluation strand for Section 3.8.2. Lighthouse audit of the production
build under mobile emulation and simulated network throttling, with
service-worker attribution established by driven browser. Measured 17
August 2026 against build index-AjooZYSG.js; supersedes the 15 August
set, retained at docs/perf/2026-08-15/.

**1. Summary of findings**

Three results, in order of importance to the argument of this
dissertation.

-   On a 0.4 Mbps connection, a first visit reaches largest contentful
    paint in 7.68 s; a repeat visit reaches it in 1.61 s, with first
    paint at 0.12 s and zero bytes of application bundle crossing the
    network.

-   The repeat-visit load is provably served by the service worker, not
    by the browser\'s HTTP cache. A full navigation performed with the
    network disconnected returned HTTP 200 with the service-worker flag
    set, and rendered the login screen.

-   Performance is insensitive to bandwidth above roughly 1 Mbps and
    degrades sharply below it. Between 1.6 Mbps and 0.4 Mbps first paint
    rises by 5.36 s, attributable almost entirely to transferring a
    single 243,724-byte bundle.

Two measurement attempts were made, found invalid, and discarded. Both
are documented in Section 6 rather than omitted.

A fourth statement is required by honesty rather than by the data: the
functional changes made on 17 August did not improve performance. Every
difference against the 15 August set lies inside run-to-run variance,
and the bundle grew by 190 bytes. The correct claim is that performance
is unchanged, and Section 7 explains why the apparent improvement in two
metrics must not be attributed to the code.

**2. Method**

Lighthouse 13.4.1 was run against the production build of the
Progressive Web App, served by the frontend-prod container on port 4173
--- the build in which the service worker is registered, unlike the
development server. Chrome ran headless on the developer machine with
the application and its backend in local Docker containers.

Throttling is Lighthouse\'s simulated (Lantern) method throughout, with
a mobile device profile and a 4× CPU slowdown held constant across every
condition, so that differences between conditions are attributable to
network characteristics alone. Command-line runs measure cold loads; the
warm condition required a scripted user flow, for the reason given in
Section 6.

Medians are reported across five runs for each command-line condition
and three iterations for the flow. Minimum and maximum are given so
run-to-run variance is visible.

Thirteen Lighthouse reports are committed under docs/perf/ in the
project repository --- five per cold condition and three flow runs, each
flow run containing both a cold and a warm navigation --- together with
the driven-browser probe and the flow script that produced them, and a
README recording the tool version, throttling parameters and what was
discarded. The superseded 15 August measurements are retained unmodified
in a dated subdirectory rather than deleted. Each report carries its
full audit trace, so every figure in this document can be independently
recomputed from the raw artifacts.

**3. Target of measurement**

The audit measures the application entry point, which is the login
screen. This is the correct target rather than merely a convenient one:
because the production bundle ships as a single JavaScript chunk with no
route-level code-splitting, the whole payload transfers on first load
regardless of the route requested. The cost of reaching the login screen
is therefore the cost of reaching any screen.

Two consequences should be stated so they do not read as errors. Speed
Index collapses onto First Contentful Paint in almost every run, because
the entry screen carries no above-the-fold imagery and paints once. And
Time to Interactive, while computed, carries zero weight in Lighthouse
13.4.1\'s performance score --- the weighting is First Contentful Paint
10, Speed Index 10, Largest Contentful Paint 25, Total Blocking Time 30,
Cumulative Layout Shift 25 --- so it is reported here for completeness
but not presented as a scored metric.

**4. Results**

All timings in seconds unless stated. Cumulative Layout Shift was 0 in
every run and is omitted from the table.

  ------------------------------------------------------------------------------------------
  **Condition**        **n**   **Perf.**   **FCP**   **LCP**   **Speed   **TBT**   **TTI**
                                                               Index**             
  -------------------- ------- ----------- --------- --------- --------- --------- ---------
  Slow 4G, 1.6 Mbps /  5       95          2.32      2.32      2.32      107 ms    2.52
  150 ms --- cold                                                                  

  Slow 3G, 0.4 Mbps /  5       57          7.67      7.67      7.67      121 ms    7.89
  400 ms --- cold                                                                  

  Slow 3G, 0.4 Mbps /  3       94          0.12      1.61      0.12      267 ms    1.61
  400 ms --- warm                                                                  

  flow harness, cold   3       58          7.68      7.68      7.68      40 ms     8.04
  navigation                                                                       
  ------------------------------------------------------------------------------------------

The final row is an internal control rather than a separate condition.
The user-flow harness performs a cold navigation before its warm one,
and that cold navigation independently reproduces the command-line cold
figure to within 0.01 s --- establishing that the two harnesses are
comparable and that the warm measurement can legitimately be set against
the command-line cold result.

Median application-bundle transfer was 243,724 bytes cold and 0 bytes
warm, against an uncompressed resource size of approximately 807 KB. The
cold figure empirically confirms the approximately 245 KB single-bundle
size previously reported without measurement. Request count falls from
seven to six on the warm navigation.

**5. Service-worker attribution**

A zero-byte transfer establishes that a resource came from cache, but
not which cache. Since the architectural claim under test concerns the
service worker specifically, and an ordinary HTTP disk cache would
evidence nothing about the design, attribution was established directly
through a driven browser rather than inferred.

  -----------------------------------------------------------------------
  **Check**                 **Result**
  ------------------------- ---------------------------------------------
  Page controlled by a      true --- controller is /sw.js
  service worker            

  Cache storage present     one cache, workbox-precache-v2, five entries

  Precache contents         index.html, the application JS and CSS
                            bundles, manifest.webmanifest, registerSW.js

  Bundle resolvable from    hit, status 200, 807,372 bytes
  cache                     

  Full navigation with      HTTP 200, served from the service worker
  network disconnected      

  Rendered result offline   login screen rendered; no console or page
                            errors
  -----------------------------------------------------------------------

One qualification is recorded because it was encountered and resolved
rather than assumed away. After the offline navigation, the browser\'s
own connectivity flag reported the network as available, which if taken
at face value would have invalidated the test. Control requests to
resources outside the precache, issued both before and after the
navigation, were rejected with a disconnection error, as were requests
to the backend API. The network was therefore genuinely unreachable at
the moment the navigation succeeded, and the connectivity flag is a
known quirk of the emulation applied to a freshly created document.

This result also retires a limitation previously recorded against this
project: that offline behaviour and the service-worker cache lifecycle
had been verified only by code inspection and API-level probing rather
than by a driven browser. That verification has now been performed.

**6. Two discarded measurements**

An intermediate network condition was attempted first, specified at 1600
Kbps with a request-latency override and labelled 3G. It was invalid on
two counts: Lighthouse\'s default mobile profile already throttles to
1638.4 Kbps, so the intended bandwidth reduction was negligible; and the
latency parameter used belongs to the DevTools throttling method rather
than the simulated method in force, so it was disregarded. The condition
was identified as invalid by an internal inconsistency --- the
supposedly slower setting returned a marginally faster median first
paint than the baseline, which no genuine bandwidth reduction can
produce.

A first attempt at the warm condition was also discarded. It used
repeated command-line invocations with storage reset disabled, on the
assumption that a service worker registered by one invocation would
persist into the next. It does not: each invocation launches a fresh
browser profile, so every supposedly warm run was in fact cold. This was
caught by the same field that later confirmed the valid result --- the
application bundle showed a full 243,534-byte transfer with no
service-worker flag --- and confirmed by inspecting the profile
directory, which contained no service worker or cache storage at all.
Had the timings been reported, they would have shown the service worker
to be ineffective, which is the opposite of the truth.

Both episodes are recorded because a method that shows how its own
errors were detected is more trustworthy than one that presents only the
runs that worked. In both cases the error surfaced through an internal
inconsistency in the data rather than through inspection of the
configuration.

**7. Interpretation**

The bandwidth threshold is sharp and its arithmetic is checkable. A
243,724-byte payload is 1,949,792 bits, requiring 4.87 s of transfer at
400 Kbps against 1.19 s at 1638.4 Kbps; the remaining portion of the
5.36 s regression is accounted for by additional round-trip latency
across connection establishment. CPU throttling was identical in both
cold conditions, confirming a network effect rather than a compute
effect.

**A confound must be declared before any figure here is compared with
the superseded 15 August set. Lighthouse records a host benchmark index
with every run: it ranged from 609.5 to 935 in August and from 425 to
1561.5 on 17 August, meaning the measuring machine was roughly
one-and-a-half to two times faster and considerably less stable. First
Contentful Paint, Largest Contentful Paint and Speed Index are modelled
analytically under simulated throttling and are largely insulated from
host speed. Total Blocking Time and the composite performance score are
not.**

Consequently the apparent movement in the slow-4G score from 93 to 95,
and in Total Blocking Time from 165 ms to 107 ms, are substantially
artifacts of host speed rather than effects of the code. Neither is
presented as an improvement in this document and neither should be
quoted as one elsewhere. The comparison that survives the confound is
the warm-against-cold contrast, which is measured within a single
browser session on a single machine and is therefore internally
controlled.

Total Blocking Time is highest in the warm condition, at 267 ms against
121 ms cold. This is expected rather than anomalous: with no network
wait, parsing and executing roughly 807 KB of JavaScript begins
immediately and is compressed into a shorter window. The warm load is
entirely CPU-bound.

Context matters for what this threshold means. Nigeria\'s median mobile
download speed was reported at 46.17 Mbps in June 2026, roughly two
orders of magnitude above the point at which the application degrades.
That is a national median weighted towards urban subscribers and is not
a description of rural conditions, and a rural-specific figure was not
obtained --- a gap in this analysis. What can be said is that the
application performs well from a degraded 3G connection upwards and
degrades materially only at throughput characteristic of 2G or
EDGE-class service.

The consequence for the dissertation\'s argument is that payload size is
the weaker version of the low-bandwidth claim. The stronger version, and
the one these measurements support, is that the application remains
usable when the network is intermittent or absent: a returning user
reaches largest contentful paint in 1.61 s on a connection that would
otherwise take 7.68 s --- a factor of 4.8, with first paint improving
sixty-six-fold --- and reaches the application at all with no connection
whatsoever.

**8. Implication for deferred code-splitting**

Route-level code-splitting has been recorded as future work on the
reasoning that first-load cost matters on slow connections. That
reasoning now carries a number: on a 400 Kbps link the single bundle
accounts for approximately 4.87 s of a 7.89 s time to interactive, and
splitting it would attack the majority of that figure.

The same measurements bound the benefit honestly in two directions. At
1.6 Mbps and above the application is CPU-bound, so splitting would
improve loading only marginally. And for any repeat visit at any
bandwidth the service worker already eliminates the transfer entirely.
Code-splitting is therefore a first-visit optimisation for the
worst-served users specifically --- a real argument for doing it, but a
narrow one rather than a general appeal to performance.

**9. A defect found during measurement**

The application\'s manifest icon is absent from the service-worker
precache and is therefore unavailable offline. The precache contains
exactly five entries --- index.html at 581 bytes, the application bundle
at 807,372 bytes, the stylesheet at 1,669 bytes, manifest.webmanifest at
380 bytes and registerSW.js at 134 bytes. Neither the manifest icon nor
the favicon appears among them.

The evidence of record is that precache listing, not a failed request. A
disconnection error was observed against the icon on one run, but
whether the browser attempts to fetch a manifest icon during a
navigation varies between runs, so the failure is intermittent while the
absence from the precache is deterministic. Any citation of this finding
should rest on the listing.

The impact is cosmetic: the shell renders correctly without the icon,
and an installed application would fall back to a default when opened
without connectivity. It is recorded as a genuine finding about the
build rather than an artefact of the measurement, and the remedy is to
extend the precache glob to include it.

**10. Limitations of this strand**

-   All network throttling is simulated. Lighthouse models network
    behaviour analytically rather than shaping real traffic, so absolute
    timings are modelled rather than observed.

-   Runs were performed on a single machine with the server on
    localhost, so no real network path, server-side latency or
    geographic distance is represented.

-   Total Blocking Time varied by more than an order of magnitude across
    runs in the fastest condition. The median is the honest summary but
    the metric is unstable at this sample size.

-   Only the application shell was measured. Authenticated routes, and
    any view containing decision-support or bioprocess output, require a
    session and were out of scope. The warm figures describe the shell
    loading, not the whole application becoming usable with data.

-   Figures characterise build index-AjooZYSG.js as at 17 August 2026
    and would need repeating after any change to the bundle. The
    superseded 15 August set is retained unmodified at
    docs/perf/2026-08-15/.

-   Host speed varied substantially between the two measurement dates
    and within the second set, as recorded in Section 7. Only
    within-session comparisons are safe; across-date comparisons of
    Total Blocking Time or the composite score are not.

-   Two harness properties are recorded so that a repeat run is not
    misled by them: the flow script does not create its own output
    directory, and the Windows command-line runner raises a permission
    error while removing its temporary browser profile after writing a
    valid report, so the presence of the report file rather than the
    exit code is the correct success signal.

**11. Sources**

-   Nigeria median mobile download speed, June 2026 --- Ookla Speedtest
    Global Index, as reported by StatiSense. Cite the Global Index
    directly rather than this secondary report before submission.

-   Nigeria internet speed ranking commentary --- The Guardian Nigeria.

*A rural-specific throughput source should be added before submission;
the national median alone does not describe the conditions this project
targets.*
