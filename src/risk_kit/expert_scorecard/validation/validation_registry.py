from __future__ import annotations

from risk_kit.expert_scorecard.models import Scorecard
from risk_kit.expert_scorecard.validation.validator import ScorecardValidator


class ValidatorRegistry:
    _validators: list[ScorecardValidator] = []

    def list_validators(self) -> list[ScorecardValidator]:
        return self._validators

    def register(self, validator_func: ScorecardValidator) -> None:
        if validator_func.name in self._validators:
            raise ValueError(
                f"Validator with name '{validator_func.name}' already registered")
        self._validators.append(validator_func)

    def validate(self, scorecard: Scorecard) -> None:
        """Run all registered validators"""
        for validator in self._validators:
            validator.validate(scorecard)
