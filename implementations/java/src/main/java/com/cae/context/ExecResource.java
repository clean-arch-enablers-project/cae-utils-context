package com.cae.context;

import lombok.AccessLevel;
import lombok.Getter;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;

import java.util.Optional;
import java.util.function.Consumer;

@Getter
@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
public class ExecResource {

    public static ExecResource of(@NonNull Object actualResource, @NonNull Consumer<ExecutionContext> finishingReaction){
        return new ExecResource(actualResource, finishingReaction);
    }

    public static ExecResource of(@NonNull Object actualResource){
        return new ExecResource(actualResource, null);
    }

    private final Object actualResource;
    private final Consumer<ExecutionContext> finishingReaction;

    public void reactToEndOfExecution(ExecutionContext executionContext){
        Optional.ofNullable(this.finishingReaction).ifPresent(action -> action.accept(executionContext));
    }

}
