from datetime import datetime, timezone
from cae_mapped_exceptions import InternalMappedException
from abc import ABC, abstractmethod
from uuid import UUID, uuid4


class ExecutionTracker:

    starting_time: datetime | None = None
    ending_time: datetime | None = None
    latency: int | None = None

    def start_tracking(self) -> None:
        if self.has_started():
            raise InternalMappedException.with_full_details(
                "Couldn't start tracking",
                "This instance already started"
            )
        self.starting_time = datetime.now(timezone.utc)

    def end_tracking(self) -> None:
        if self.has_started():
            self.ending_time = datetime.now(timezone.utc)
        else:
            raise InternalMappedException.with_full_details(
                "Couldn't start tracking",
                "This instance hasn't started yet"
            )

    def has_started(self) -> bool:
        return self.starting_time is not None

    def is_complete(self) -> bool:
        return self.ending_time is not None

    def get_latency(self) -> int:
        if self.is_complete():
            if self.latency is not None:
                return self.latency
            assert self.starting_time is not None
            assert self.ending_time is not None
            delta = self.starting_time - self.ending_time
            return int(delta.total_seconds() * 1000)
        else:
            raise InternalMappedException.with_full_details(
                "Couldn't get latency",
                "This instance has either not started nor ended yet"
            )


class GenericExecutionManager(ExecutionTracker):

    subject: str | None = None
    inbound: bool | None = None
    exception: Exception | None = None
    input: object | None = None
    output: object | None = None

    def set_subject_and_start_tracking(
            self, subject: str,
            inbound: bool
    ) -> None:
        if self.has_started():
            raise InternalMappedException(
                "Couldn't set subject and start tracking",
                "The execution context you tried to start was already used"
            )
        self.subject = subject
        self.inbound = inbound
        self.start_tracking()

    def complete(self) -> None:
        self.end_tracking()

    def complete_with_ex(self, exception: Exception) -> None:
        self.end_tracking()
        self.exception = exception

    def calculate_latency(self) -> int:
        return self.get_latency()

    def was_successful(self) -> bool:
        if self.is_complete():
            return self.exception is None
        raise InternalMappedException(
                "Couldn't check whether execution was successful",
                "It wasn't complete"
            )


class StepInsight(GenericExecutionManager):

    @classmethod
    def create_new_of(cls, subject: str):
        new_insight = StepInsight()
        new_insight.set_subject_and_start_tracking(subject, False)
        return new_insight

    def format_as_text(self) -> str:
        latency = self.calculate_latency()
        header_sec: str = f"{self.subject}'s insights: ({latency}ms) "
        success_sec: str = "no exception has been thrown"
        error_sec: str = "an exception has been thrown along the way: "
        if self.was_successful():
            status_section = success_sec
        else:
            status_section = error_sec + self.exception.__str__()
        return header_sec + status_section


class Actor(ABC):

    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def get_scopes(self) -> list[str]:
        pass


class ExecutionContext(GenericExecutionManager):

    def __init__(
            self,
            correlation_id: UUID,
            actor: Actor | None = None
    ):
        super().__init__()
        self.correlation_id = correlation_id
        self.actor = actor
        self.step_insights: list[StepInsight] = []

    @classmethod
    def create_new_of(cls, correlation: UUID):
        return cls(
            correlation_id=correlation
        )

    @classmethod
    def create_new_of_str(cls, correlation: str):
        return cls(
            correlation_id=UUID(correlation)
        )

    @classmethod
    def create_new_with_actor(
        cls,
        correlation: UUID,
        actor: Actor
    ):
        return cls(
            correlation_id=correlation,
            actor=actor
        )

    @classmethod
    def create_new_on_str_with_actor(
        cls,
        correlation: str,
        actor: Actor
    ):
        return cls(
            correlation_id=UUID(correlation),
            actor=actor
        )

    @classmethod
    def create_new_random_with_actor(
        cls,
        actor: Actor
    ):
        return cls(
            correlation_id=uuid4(),
            actor=actor
        )

    @classmethod
    def create_new_random(cls):
        return cls(
            correlation_id=uuid4()
        )

    def add_step_insights_of(self, step_name: str) -> StepInsight:
        if self.has_started():
            new_step_insight = StepInsight.create_new_of(step_name)
            self.step_insights.append(new_step_insight)
            return new_step_insight
        raise InternalMappedException(
            "Couldn't add step insight",
            "The execution context hasn't started yet"
        )
