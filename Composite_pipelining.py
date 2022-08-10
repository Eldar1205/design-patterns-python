from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Collection


class Dataset:
    # A dataset class, e.g. like pandas Dataframe

    def merge(self, other: Dataset) -> Dataset:
        # merges the other Dataset into this one
        return self

class IDatasetTransformer(ABC):
    @abstractmethod
    def transform(self, dataset: Dataset) -> Dataset:
        pass

class AddTotalsRowTransformer(IDatasetTransformer):
    def transform(self, dataset: Dataset) -> Dataset:
        # Summarize all numeric columns of dataset and add a new row with the totals
        return dataset

class ColumnsSelectorTransformer(IDatasetTransformer):
    def __init__(self, columns_to_keep: Collection[str]) -> None:
        self.__columns_to_keep = columns_to_keep

    def transform(self, dataset: Dataset) -> Dataset:
        new_dataset = ... # Remove columns from dataset without modifying the original so the other columns aren't lost
        return new_dataset

# Functional programming!
class FunctionTransformer(IDatasetTransformer):
    def __init__(self, transformer: Callable[[Dataset], Dataset]) -> None:
        self.__transformer = transformer

    def transform(self, dataset: Dataset) -> Dataset:
        return self.__transformer(dataset)

# We can compose transformers by chanining them to a pipeline because their input & output are the same type
# The class accepts a transformer function to wrap in FunctionTransformer on behalf of Pipeline class users
class Pipeline(IDatasetTransformer):
    def __init__(self, *transformations: IDatasetTransformer) -> None:
        self.__transformations: list[IDatasetTransformer] = list(*transformations)

    def append(self, transformer: IDatasetTransformer) -> Pipeline: # return self for method chaining
        self.__transformations.append(transformer)

        return self

    def transform(self, dataset: Dataset) -> Dataset:
        for transformation in self.__transformations:
            dataset = transformation.transform(dataset)

        return dataset

def main() -> None:
    orig_employees_ds: Dataset = ... # Load from somewhere, e.g. CSV or DB

    # You'd wish your HR department would run this for real..
    rewards_pipeline = Pipeline(
        ColumnsSelectorTransformer(("salary", "bonus")), # Doesn't modify the original dataset, important to not lose the other columns
        FunctionTransformer(lambda ds: ds * 10) # Will be wrapped in FunctionTransformer for us
    )

    # Pipelines are themselves transformers, can be stages in a higher level pipeline!
    summary_after_rewards_pipeline = Pipeline(rewards_pipeline)

    # Composite design pattern doesn't require immutability, you can add stages to an existing pipeline
    summary_after_rewards_pipeline.append(FunctionTransformer(orig_employees_ds.merge)).append(AddTotalsRowTransformer())

    updated_employees_ds = summary_after_rewards_pipeline.transform(orig_employees_ds)

    print(updated_employees_ds)
