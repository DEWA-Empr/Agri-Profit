**AGRI-PROFIT --- Usability Session Run-Sheet**

Facilitator script for the dry run and the evaluator sessions. Companion
to the Usability Evaluation Pack (Section 3.8.4).

**The one rule that matters**

**Do not fix things you find. Not in the dry run, not during a
session.**

The instinct before showing anyone your work is to tidy it first. Resist
it completely. A heuristic evaluation exists to surface exactly the
confusions you would otherwise polish away, and every issue you quietly
fix beforehand is a finding you have destroyed and cannot report. A
rough edge an evaluator trips over is not an embarrassment --- it is the
data.

The single exception: a hard blocker. A crash, a server error, or a task
that is literally impossible to complete. Fix those, because otherwise
the evaluator cannot proceed and you lose the whole session. Everything
else --- confusing labels, awkward flows, unclear errors, ugly layout
--- gets written down and left alone.

**Part 1 --- The dry run**

You play the evaluator. Same six tasks, same order, but your purpose is
different: you are looking for blockers, timing the session, and
rehearsing the offline task. Budget 45 minutes. Do it at least a day
before the first real session so there is time to fix any hard blocker
you find.

**Setup**

Use the production build. The development server registers no service
worker, which would make task 6 meaningless.

docker compose \--profile prod up -d \--build frontend-prod

curl -I http://localhost:4173 expect HTTP 200

curl -s http://localhost:8000/health expect status healthy

Then open http://localhost:4173 in Chrome and register a throwaway farm.

**What to record as you go**

-   How long each task takes. Use your phone. You need this to know
    whether 25 minutes is realistic.

-   Anything that stops you dead --- note it, decide fix-or-record using
    the rule above.

-   Anything that made you hesitate, even briefly. If it catches you,
    and you built it, it will stop them.

-   Whether every task in the pack is actually possible. If one is not,
    decide now whether to fix it or to mark it N/A, rather than
    discovering it mid-session.

**Rehearse the offline task properly**

Task 6 will not work the way you expect. The application is served from
localhost, so switching off WiFi disconnects nothing. Stop the backend
instead, which leaves the page served while making the API unreachable
--- exactly the condition the offline queue is designed for.

docker compose stop backend API now unreachable

\...evaluator records an activity; a pending-sync indicator should
appear\...

docker compose start backend queue should flush on reconnect

Confirm in the dry run that the pending indicator actually appears and
that the entry lands after restart. You run these commands, never the
evaluator. Have the terminal open and ready before each session so there
is no fumbling.

**End state**

By the end of the dry run you should know: total session length, which
tasks are quick and which are slow, any hard blocker fixed, and a
written list of your own observations --- kept separately, because your
findings are not evaluator findings and must not be mixed into their
issue log.

**Part 2 --- Running a real session**

**Before they arrive**

-   Stack up, both URLs confirmed responding.

-   Browser storage cleared --- see Part 3, this matters more than it
    sounds.

-   Printed pack: Part A task script, Part B heuristic checklist, Part C
    the SUS questionnaire.

-   Blank paper for your own notes. The pack has no observer sheet.

-   Terminal open, ready for the backend stop and start.

-   Phone stopwatch ready.

**What to say at the start**

Say roughly this, in your own words:

*\"Thank you for doing this. I\'m testing the system, not you --- if
anything is confusing, that\'s a problem with my design, not with you,
and it\'s exactly what I need to find out. Please think aloud as you go,
so I can hear what you\'re expecting. I won\'t help unless you\'re
completely stuck; if you are, just say so and we\'ll move on. It\'ll
take about 25 minutes. I\'ll be writing notes the whole time --- that\'s
normal, not a sign anything is wrong. Everything you say is recorded
against your name and role for my project write-up, and you can stop at
any point.\"*

That last sentence is your consent statement. Say it, and note on the
sheet that you did.

**While they work --- the discipline**

**This is the hard part, and it is where small panels are usually
ruined.**

-   Do not help. Every explanation you give destroys a data point. If
    they cannot find something, that IS the result --- write down where
    they looked first.

-   Do not defend the design. If they criticise something, say \"thank
    you, that\'s useful\" and write it down. Arguing changes how they
    rate everything afterwards.

-   Let silence sit. Ten seconds of someone staring at a screen feels
    unbearable when you built it, and it is one of the most informative
    things you will observe.

-   Sit beside or slightly behind them, not opposite. Facing someone
    across a screen turns it into a test of them.

-   Write verbatim quotes, not summaries. \"I don\'t know what unit cost
    means here\" is worth more in your Chapter Four than \"confused by
    DSS labels\".

**The offline task**

When they reach task 6, stop the backend from your terminal without
narrating it. Let them attempt the entry and observe what they notice.
Ask afterwards whether they believed it had saved, and why --- their
answer tells you whether the pending indicator communicates anything at
all. Then restart the backend and let them confirm.

**Parts B and C --- leave them alone**

Hand over the heuristic checklist and the SUS questionnaire and then
physically turn away, or step out of the room. Someone filling in \"I
found the system unnecessarily complex\" with the author watching over
their shoulder will score it more kindly, and that bias is well
documented. Collect the sheets when they are done.

**Part 3 --- Between evaluators**

**Clear the browser\'s site data before the next person. This is not
tidiness --- it is required for the data to be valid.**

Your own limitations chapter records that the offline write queue is not
identity-scoped: it is not cleared on logout, so an unsynced entry left
by one evaluator can flush under the next evaluator\'s token and land in
the wrong farm. Task 6 deliberately creates queued entries, so this will
happen unless you clear storage between sessions.

In Chrome: DevTools, Application tab, Storage, \"Clear site data\". Then
close the tab and reopen it. Each evaluator registers their own fresh
farm.

Worth noting: having anticipated this because you documented the
limitation yourself is a good answer if an examiner asks how you kept
the sessions independent.

**Part 4 --- Afterwards**

-   Collect all three sheets per evaluator, with name and role filled
    in.

-   Score each SUS immediately while it is fresh: odd items score
    (response − 1), even items score (5 − response), sum the ten,
    multiply by 2.5. Range 0--100, and it is not a percentage.

-   Report the mean across evaluators as indicative, never as
    statistically representative, and give the individual scores
    alongside it.

-   Merge the issue logs, deduplicate, and keep the highest severity
    rating any evaluator gave each issue.

-   Photograph or scan every completed sheet. These are the raw
    instruments an examiner may ask to see, and paper goes missing.

**If something goes wrong mid-session**

  -----------------------------------------------------------------------
  **Situation**            **What to do**
  ------------------------ ----------------------------------------------
  A task turns out to be   Mark it \"N/A -- not built\" as the pack
  impossible               allows, move on, and record it as a finding.
                           Do not improvise a workaround.

  The evaluator asks how   \"I\'d rather see what you\'d do without me.\"
  something works          If they are truly stuck after a reasonable
                           pause, note it as a task failure and move on.

  The app errors or        Note exactly what they did immediately
  crashes                  beforehand, restart if needed, and continue
                           from the next task. A crash is a finding, not
                           a lost session.

  They finish early        Ask what they would want the system to do that
                           it does not. Unprompted answers here are often
                           the most useful thing in the whole session.

  They ask about a feature Say it is not built and move on. Do not
  you know is unbuilt      demonstrate anything outside the six tasks ---
                           it contaminates their impression before they
                           rate it.
  -----------------------------------------------------------------------
