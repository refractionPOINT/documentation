# Query Console UI

Many critical security operations require a query console with strong search functionality. It enables analysts to query large volumes of telemetry, logs, and events for investigations, hunting, and incident response.

LimaCharlie's Query Console (with integrated Search) brings this functionality to the SecOps Cloud Platform. We've combined familiar query workflows with features like type-ahead syntax, time range selection, and detection-as-code conversion. This lets your team quickly investigate alerts, analyze data across tenants, and extend LimaCharlie into other modern SIEM use cases.

All events ingested into LimaCharlie are retained and available for analysis. Data is parsed at ingest and saved in LimaCharlie hot storage. Search queries this large volume of telemetry for matches within the time frame you provide. Searches are billed based on the number of events scanned (measured in millions). See Pricing for specifics.

## Permissions

To view and operate the Query Console, the following permissions are required:

  * `insight.evt.get` for search
  * `org.get` for schema service access
  * `query.set` for saving queries
  * `query.get` for reading a list of queries (if you don't have this set you will see an error saying you need `query.get.mtd`, but this is the permission you need)
  * `query.del` for editing or deleting queries (editing is creating a new one and removing the old one)

## UI Element Overview

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(338).png)

  1. **Source:** Select Events (everything that had been injected from endpoints and XDR sources, default), Detections, or Platform Audit events as the data source for the search.

  2. **Query editor:** Enter a LimaCharlie Query Language (LCQL) query to include:

    1. _Sensor Selector -_ precisely define the sensors that produced the desired events.

    2. _Event Type_ \- filter results to only return specific types of events.

    3. Filter - the actual query filter using individual fields and operations on top of them.

    4. Projections (optional) - control output columns, sort results via `ORDER BY` and/or aggregate the data with `GROUP BY` , `COUNT`, `COUNT_UNIQUE` and more. See LCQL reference and Examples for details.

  3. **Time period:** Set the searchable time period using three options: last [time period], around [time frame], and absolute "from start to finish".

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(340).png)

     * Enter a time `16:00`, or day and time `2025-01-16 08:52:54`, using most common time formats. For example:

       * From `33m` to `now` \- last 33 minutes

       * Around `2025-01-16 08:52:54` +- `15 minutes` \- 15 minutes before and after the specified time stamp

       * From `10am` to `1:30pm`

**Note:** All times are shown according to the timezone selected by the user in User Settings.

  4. **Available Fields:** Managed data exploration

    1. Schema fields - a list of all the fields associated with ingested events.

    2. Event types - event types present in the returned portion of the query. As more data is churned to complete the specified time frame more event types may appear.

    3. Query fields - event fields present in the _portion of the result already fetched by the query_ , with a count of total occurrences. Clicking on the event field opens a details panel. From here you can add a term to the query.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(341).png)

    4. Table columns: control the columns displayed in Table View.

Note: While the schema fields are always available, the event types and query fields are only shown for portion of the time frame _searched so far_. As more data is churned in the background (to complete your selected time frame), more event types and fields may appear.

  5. **Query status:** Shows the state of your query in real time, highlighting any existing syntax errors or providing a cost estimate if the query is properly formed.

As the query runs the status displays progress, query status, and a running total of the cost accrued.

_Query cost estimation:_ Queries are charged by the amount of data churned, measured and billed per one million events evaluated. This estimation shows the "at most" cost of a query for the selected time range. Only retrieved data is chargeable.

_Performance tuning:_ The better tuned the query, the faster the search and lower the cost. Using Sensor Selector and Event Type to precisely target the desired telemetry will increase search speeds and lower costs.

  6. **Histogram:**

When a search is run, a histogram appears below the query field showing the distribution of events over time. The portion with a vertical bar chart represents results that have been retrieved so far. The non-bar chart portion shows the total number of events in the selected time frame. The histogram shows the progress of the search through the time frame. As you paginate through the search, more events are evaluated, and more bars appear to signify the progress through the time frame.

  7. **Search results:** displays results in two views, **timeline** and **table**. Timeline view shows matching events with the most recent on top. Table view provides a way to sort results into desired columns. Find the desired field in Query Fields and use the `pin` icon to add it as a column.

    1. A **Tab Columns** section appears in the **Fields** sidebar when table view is selected. Columns can be viewed or removed here.

    2. **Event Details** allows you to click on an event and perform applicable event actions like **Build a D &R Rule**.

    3. **Download** all the events you've retrieved in a [.ndjson format](https://github.com/ndjson/ndjson-spec). The automatic download of the entire time range is coming soon.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(342).png)

  8. **Saving Queries and Query Library.** A query can be saved in your private user library or shared via an org library. Use the library to browse queries and load the desired one to the query editor.
