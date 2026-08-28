**AGRI-PROFIT --- Hosting-Cost Analysis**

Evaluation strand for Section 3.8.3. Monthly operating cost estimated
from the platform\'s measured resource footprint and published provider
pricing. Revised 15 August 2026 against measurement; supersedes the
earlier reasoned estimate.

**1. Purpose and method**

Objective 4 requires an assessment of cost-effectiveness. A production
deployment was outside the scope of this study, so operating cost is
estimated rather than incurred. The method is: measure the platform\'s
actual resource consumption in the running Docker stack; select the
smallest commodity instance that accommodates it with reasonable
headroom; and apply published provider pricing as at August 2026.

An earlier version of this analysis reasoned the footprint from the
known composition of each container rather than measuring it. Those
estimates proved substantially too high, and are superseded here by
measurement. The difference is material to the conclusion and the
correction is recorded in Section 3.

**2. Measured resource footprint**

Container memory and CPU were sampled from the running stack, at rest
and across a backend restart. Figures are reported as ranges across two
separate container instances, since an approximately 11% variation was
observed between them.

  -----------------------------------------------------------------------
  **Component**         **Measured      **Notes**
                        memory**        
  --------------------- --------------- ---------------------------------
  FastAPI backend       145.5--161.5    Steady state at rest,
                        MiB             approximately 0.2% CPU. Peak
                                        during startup was 145.5 MiB,
                                        reached 8.19 s after restart and
                                        immediately before startup
                                        completed at 8.57 s.

  PostgreSQL 15         33.4--41.3 MiB  Steady state at rest,
                                        approximately 0.0% CPU, against
                                        the seeded demonstration dataset.

  Measured subtotal     178.9--202.8    The two containers exercised
                        MiB             during measurement.

  Static PWA server     not measured    The frontend-prod container was
                                        not running during sampling. A
                                        Node process serving a built
                                        bundle would add on the order of
                                        50--80 MiB; nginx or Caddy would
                                        add closer to 15 MiB.

  OS and container      not measured    Linux with the Docker daemon,
  runtime                               conventionally 300--400 MiB.
  -----------------------------------------------------------------------

A sampling caveat is required. Memory was captured by repeated
single-shot polling, giving seven samples across a 14.2 s startup window
at a mean interval of 2.37 s. This is not continuous coverage, and the
widest gap --- 4.11 s --- falls precisely across the steepest part of
the climb, from 26 MiB to 100 MiB. The 145.5 MiB startup peak should
therefore be read as a lower bound on the true maximum, not as the
maximum itself.

**3. A correction: the machine-learning tier is not the cost driver**

The superseded version of this analysis argued that importing
scikit-learn and holding a fitted RandomForest in process dominated
memory, that the train-on-boot step set the peak against which the
instance must be sized, and that externalising the model artifact would
roughly halve the compute cost. Measurement does not support that
argument.

The entire backend process --- Python runtime, FastAPI, SQLAlchemy,
numpy, scikit-learn, and the trained model together --- occupies 145 to
162 MiB. Whatever share of that the machine-learning tier accounts for,
the absolute figure is far too small to influence the choice of
instance. The reasoned estimate was wrong by a factor of roughly three,
and the conclusion drawn from it was wrong in kind rather than merely in
degree.

What the measurement does show is that the train-on-boot step costs
startup time rather than memory: the backend takes 8.57 s from restart
to accepting traffic, of which the memory climb from 26 MiB to its
plateau occupies roughly the first eight seconds. On a single-instance
deployment with no redundancy, that is 8.6 s of unavailability on every
restart or redeployment. The architectural case for externalising the
model artifact therefore stands, but it rests on availability and the
ability to run multiple replicas, not on hosting cost.

**4. Storage and bandwidth are not cost drivers either**

A paired record --- one Operational Log with its Financial Transaction
--- occupies on the order of 1 KB including index overhead. A
medium-scale farm logging five activities a day generates roughly 1,825
paired records a year, or about 1.8 MB. At that rate the 50 GB volume
included with an entry-level instance would hold tens of thousands of
farm-years before storage became a consideration.

Bandwidth is similarly immaterial. The application bundle is 243,534
bytes and is served from the service-worker precache on every visit
after the first, so it crosses the network once per device; API
responses are measured in kilobytes. Against the multi-terabyte transfer
allowances included with every plan surveyed, egress is effectively free
at any plausible pilot scale.

This matters to the argument as well as the arithmetic. The platform\'s
cost profile is dominated by a fixed monthly instance charge rather than
per-farm consumption, so cost per farm falls almost linearly with the
number of farms served. That is the structural opposite of the per-seat
licensing which this dissertation identifies as excluding smallholders
from existing farm management systems.

**5. Provider comparison**

Given a measured subtotal under 205 MiB for the application containers,
a 2 GB instance accommodates the stack with substantial headroom for the
operating system and for the filesystem cache PostgreSQL relies on. The
4 GB tier recommended by the superseded estimate is not required. None
of the providers surveyed operates a data centre in Nigeria.

  ---------------------------------------------------------------------------
  **Provider**   **Plan**    **vCPU / **SSD /      **Price /  **Nearest
                             RAM**    transfer**   month**    region**
  -------------- ----------- -------- ------------ ---------- ---------------
  Hetzner Cloud  CX22        2 / 4 GB 40 GB / 20   €3.79      Falkenstein or
                                      TB                      Helsinki

  DigitalOcean   Basic       1 / 2 GB 50 GB / 2 TB \$12.00    London or
                                                              Frankfurt

  Amazon         2 GB bundle 2 / 2 GB 60 GB / 3 TB \$12.00    Cape Town or
  Lightsail                                                   Europe

  DigitalOcean   Basic       2 / 4 GB 80 GB / 4 TB \$24.00    London or
                                                              Frankfurt
  ---------------------------------------------------------------------------

Hetzner is markedly cheaper at equivalent specification but has no
African presence. Amazon is the only surveyed provider with an African
region, though whether the Cape Town region carries these bundles was
not confirmed and should be verified before it is relied upon. Note also
that geographic proximity is not network proximity: West African traffic
to Europe is carried by well-provisioned submarine cable, and no latency
claim in either direction is made here because none was measured.

**6. Estimated monthly cost**

Taking the 2 GB tier at \$12 as the reference configuration, and adding
the operational items a real deployment requires that the current build
does not provide:

  ------------------------------------------------------------------------
  **Line item**                     **USD / month**    **NGN / month**
  --------------------------------- ------------------ -------------------
  Instance (2 GB RAM, 50 GB SSD)    \$12.00            ₦16,327

  Automated snapshot backups (\~20% \$2.40             ₦3,265
  of instance)                                         

  Domain name (amortised from       \$1.00             ₦1,361
  \~\$12/year)                                         

  TLS certificate (Let\'s Encrypt)  \$0.00             ₦0

  Estimated total                   \$15.40            ≈ ₦20,950
  ------------------------------------------------------------------------

Naira conversions use the Central Bank of Nigeria rate of ₦1,360.58 to
the US dollar as at 12 August 2026. The parallel-market rate on 13
August 2026 was ₦1,425, so naira figures are indicative rather than
exact. Selecting Hetzner at equivalent specification would reduce the
instance line further; those figures are quoted in euro and are not
converted, as no dated euro-to-naira rate was obtained.

**7. Cost per farm at scale**

Because cost is dominated by a fixed instance charge, the meaningful
figure for the cost-effectiveness argument is cost per farm served.

  ------------------------------------------------------------------------
  **Farms per instance** **NGN / farm / month**   **Assumption**
  ---------------------- ------------------------ ------------------------
  50                     ₦419                     Early pilot.

  100                    ₦210                     Small cooperative.

  200                    ₦105                     Conservative
                                                  single-instance
                                                  capacity.

  500                    ₦42                      Upper bound before
                                                  single-instance limits
                                                  bind.
  ------------------------------------------------------------------------

These tenancy figures are reasoned, not measured. They assume the low
write rate characteristic of manual data entry, on the order of five
records per farm per day, and no concurrent-load testing has been
performed to establish the true ceiling. The single-instance assumptions
documented as limitations of this platform, together with the unresolved
N+1 query on the ledger listing, would bind well before hardware
capacity did.

**8. What this estimate excludes**

-   Staff time --- administration, support, onboarding and incident
    response --- which is excluded entirely and would dominate total
    cost of ownership in any real deployment.

-   Managed database service, which would replace the self-hosted
    PostgreSQL container at roughly double the instance cost in exchange
    for backup and recovery guarantees.

-   Observability: metrics, tracing and alerting, which the current
    build does not provide.

-   Secret management, and any compliance or data-residency requirement
    that might mandate in-country hosting.

-   Messaging aggregator fees, which would apply per message if the
    feature-phone channel were connected to a live carrier gateway.

-   The farmer\'s own data cost. The bundle crosses the network once per
    device and is served from the service-worker precache thereafter, so
    recurring cost to the user is small --- but quantifying it in naira
    requires a cited source for Nigerian prepaid data pricing, which
    this analysis does not have.

**9. Limitations of this analysis**

Two components of the footprint were not measured: the static file
server, which was not running during sampling, and the host operating
system with its container runtime. Both are conventionally sized and
neither is likely to alter the choice of instance tier, but the total
remains part-measured and part-assumed.

Startup memory was sampled at roughly two-second intervals rather than
continuously, so the reported peak is a lower bound. Memory was observed
to vary by approximately 11% between two container instances of the same
image, so single figures are avoided in favour of ranges.

Provider prices are list prices captured on a single date, exclusive of
tax, committed-use discounts and free-tier allowances. No provider was
contacted, no quotation obtained, and no Nigerian provider\'s pricing
retrieved, so in-country hosting is discussed qualitatively but not
costed.

Finally, this prices the platform as it exists: a single-instance
deployment with no redundancy, in which every restart costs 8.6 s of
unavailability. A configuration meeting ordinary production expectations
for availability would cost several times this figure, and the distance
between the two is itself part of the honest account of what has been
built.

**10. Sources**

-   Hetzner Cloud CX plan specifications and pricing --- hetzner.com

-   DigitalOcean Droplet pricing --- digitalocean.com/pricing/droplets

-   Amazon Lightsail pricing --- aws.amazon.com/lightsail/pricing

-   USD/NGN Central Bank of Nigeria rate, 12 August 2026, and
    parallel-market rate, 13 August 2026 --- ngnrates.com

*All prices retrieved 15 August 2026. Provider pricing pages should be
re-checked and the retrieval date restated before submission.*
