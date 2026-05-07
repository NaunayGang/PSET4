"Module for presenters in the application layer. Presenters are responsible for formatting the output data from the use cases into a format that can be easily consumed by the presentation layer (e.g., REST API, GraphQL, etc.). This module can include presenters for incidents, logs, and any other entities that need to be presented to the user."

from .incident_presenter import IncidentPresenter as IncidentPresenter
