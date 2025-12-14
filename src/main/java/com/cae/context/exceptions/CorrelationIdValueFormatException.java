package com.cae.context.exceptions;

import com.cae.mapped_exceptions.specifics.InputMappedException;

public class CorrelationIdValueFormatException extends InputMappedException {
    public CorrelationIdValueFormatException(String stringValue) {
        super("The string value '"+stringValue+"' cant be used as a correlation ID. Correlation IDs must be unique. For that reason it is decided they must be in UUID format.");
    }
}
