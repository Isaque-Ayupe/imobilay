## 2024-03-25 - ContextStore Serialization Bottleneck
**Learning:** In a multi-agent environment using deep copies of large contexts for immutability, full Pydantic model serialization and deserialization (`deepcopy(self.model_dump())` followed by `ContextStore.model_validate(data)`) creates a major performance bottleneck for each patch application.
**Action:** Use Pydantic's built-in `model_copy(deep=True)` and set nested properties natively using `getattr` and `setattr` instead of rebuilding entire nested structures using dictionary key traversal. This avoids full conversion loops.
