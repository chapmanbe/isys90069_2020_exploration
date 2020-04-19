from . emutils import table_options
import ipywidgets as ipw
from markdown import markdown


## `cenus_events`


text = {
"census_events": """This table describes change of location events during the patient's hospitilazations, that is the admission to and discharge from a particular ICU unit. (Remember that these data are for ICU patients only)."""

, "chart_events": """## `chart_events`

This table describes when values are added into the patient's chart, usually by a nurse or a respiratory therapist. Examples of these values would include vitals (pulse, respiration rate, blood pressure) or the results of lab tests (for example, blood Potassium levels). `chart_events` have names (`label`) and are grouped into `categories`

### Key columns:

* `label`: This is the name given to the chart event. Most interesting plots would be created by filtering the data based on particular chart event names, like `Arterial BP`

* `value1`: chart events with categorical outcomes have their value stored in the `value1` column. An example of categorical values are those associated with the `label` `Behavior` which has values
    * `Angry`
    * `Anxious`
    * `Appropriate`
    * `Calm`
    * `Restless`
    * `Sedated`
    * `Sleeping`

* `value1num`: chart events with numerical outcomes have their numeric value stored in `value1num`. Example: `label` `Glucose (70-105)` has numeric values ranging from around 100 to 180.
* `value2num`: Some chart events include two values. A good example of this is blood pressure, which stores the systolic values in `value1num` and the diastolic values in `value2num`"""

, "demographic_events": """## `demographic_events`

This table records demographic dat at the time of admission, plus also describes the route for admission (e.g. `EMERGENCY ROOM ADMIT`, `ELECTIVE`)"""

, "icustay_events": """## `icustay_events`

This table provides information about when and where patients were in a particular ICU.
"""

, "io_events": """## `io_events`

This table provides information about patient input and output in terms volumes, primarily fluids.

### Key columns:

* `category`: The general category of `io_events` including `IV Infusions`, `Missing` (not specified), `PO/Gastric`, and `Tube Feeding`
* `label`: The spcecific name of an `io_event` such as `Urine Out Foley`
* `volume`: The numeric value of the volume. The units of measurement are provided in the column `volumeuom`."""

, "lab_events" : """## `lab_events`

This table provides the results of lab tests, such as blood chemistry or hematology tests. A question to consider: are these values or some of these values duplicated in `chart_events`?

### Key columns:

* `test_name`: The local institution, human name for the test
* `loinc_description`: The LOINC standard name for the test.
* `value`: categorical value results
* `valuenum`: numeric value results
* `flag`: was the test normal or abnormal. Normal test values have a missing value `None`.
* `category`: general categories of the tests
* `fluid`: tissue/fluid source for the test."""

, "med_events" : """## `med_events`

This table provides information about medications administered to the patient. Almost all the medications in the selected patients are administered with a `route` value of `IV Drip`.

### Key columns:

* `medname`: The name of the medication.
* `cgid`: The ID of the caregiver administering the medication. """

, "microbiology_events" : """## `microbiology_events`

This table records results of testing for the presence of particular bacteria and their sensitivity to particular antibiotics. The table needs to be understood in terms of three columns simultaneously, as the results are reported in terms of the presence of an organism `organism_name` and how that organism reacts to a particular antibiotic `antibiotic.` The nature of that reaction is providing in `interpretation`: the organism is either sensitive `S` (is killed by the antibiotic) or resistant `R` (is immune to the antibiotic). If no organisms are identified, all the values are missing."""

, "note_events" : """## `note_events`

This table stores all the written documentation about a patient. There are three `categories` of notes `Nursing/Other` these are the most common, `RADIOLOGY_REPORT` reports created by radiologists interpreting medical imaging procedures, `DISCHARGE_SUMMARY` the detailed note created when a patient is discharged (including when they die). Even though discharge summaries are created at the *end* of the hospitalization, in the database they are dated at the beginning of the hospitalization. Common `Other` notes are respiratory therapist notes."""

, "procedure_events" : """## `procedure_events`

This table records when billable procedures were performed, seemingly distinct from radiology procedures.

### Key columns:

* `description`: the name of the procedure."""

}

descriptions = ipw.Tab()
children = [ipw.HTML(value=markdown(text[t])) for t in table_options]
for i in range(len(table_options)):
    descriptions.set_title(i,table_options[i])
descriptions.children = children
