from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Collection


class Dataset:
    # A dataset class, e.g. like pandas Dataframe

    def merge(self, other: Dataset) -> Dataset:
        # merges the other Dataset into this one
        return self

# A pipeline using Decorators Chain
class IDatasetTransformer(ABC):
    @abstractmethod
    def transform(self, dataset: Dataset) -> Dataset:
        pass

# Meant to serve as the sink of the Decorators Chain, doesn't inherit DatasetTransformerStepBase because no next step
class IdentityTransformer(IDatasetTransformer):
    def transform(self, dataset: Dataset) -> Dataset:
        return dataset

# A step in the chain, base class for implementing a transformer decorator
class DatasetTransformerStepBase(IDatasetTransformer, ABC):
    def __init__(self, next_step: IDatasetTransformer | None = None) -> None:
        self.__next_step = next_step or IdentityTransformer()
        
    def transform(self, dataset: Dataset) -> Dataset:
        return self.__next_step.transform(dataset)
    
    def set_next_step(self, next_step: IDatasetTransformer) -> None:
        self.__next_step = next_step
        
# Allows us to focus on certain columns we want to transform in the dataset and not affect the rest
class ColumnsSelectorTransformer(DatasetTransformerStepBase):
    def __init__(self, columns_to_keep: Collection[str], next_step: IDatasetTransformer | None = None) -> None:
        super().__init__(next_step)
        self.__columns_to_keep = columns_to_keep

    def transform(self, dataset: Dataset) -> Dataset:
        new_dataset = ... # Remove columns from dataset without modifying the original so the other columns aren't lost
        return super().transform(new_dataset)

# Functional programming! Allows us to turn a function to a transformer, no need for new class every time we need a one-liner
class FunctionTransformer(DatasetTransformerStepBase):
    def __init__(self, transformer: Callable[[Dataset], Dataset], next_step: IDatasetTransformer | None = None) -> None:
        super().__init__(next_step)
        self.__transformer = transformer

    def transform(self, dataset: Dataset) -> Dataset:
        return super().transform(self.__transformer(dataset))

# Eventually we want to sum up rows and calculate totals
class AddTotalsRowTransformer(DatasetTransformerStepBase):   
    def transform(self, dataset: Dataset) -> Dataset:
        # Summarize all numeric columns of dataset and add a new row with the totals
        return super().transform(dataset)

class Pipeline(IDatasetTransformer):
    def __init__(self, *transfomers: DatasetTransformerStepBase) -> None:
        self.transformers: list[DatasetTransformerStepBase] = []

        for transformer in transfomers:
            self.append(transformer)

    def append(self, transformer: DatasetTransformerStepBase) -> Pipeline:
        transformer.set_next_step(IdentityTransformer())

        if len(self.transformers) > 0:
            self.transformers[-1].set_next_step(transformer)

        self.transformers.append(transformer)

    def transform(self, dataset: Dataset) -> Dataset:
        return self.transformers[0].transform(dataset)

def main() -> None:
    # You'd wish your HR department would run this for real..
    orig_employees_ds: Dataset = ... # Load from somewhere, e.g. CSV or DB

    # Decorators chain pipeline: Option #1 using constructors
    employees_pipeline = ColumnsSelectorTransformer(
        ("salary", "bonus"),  # Doesn't modify the original dataset, important to not lose the other columns
        FunctionTransformer(
            lambda ds: ds * 10, # Will be wrapped in FunctionTransformer for us
            FunctionTransformer(
                orig_employees_ds.merge,
                AddTotalsRowTransformer())))

    # Decorators chain pipeline: Option #2 using set_next_step
    rewards_columns_transformer = ColumnsSelectorTransformer(("salary", "bonus"))
    multiply_by_10_transformer = FunctionTransformer(lambda ds: ds * 10) 
    merge_to_orig_ds_transformer = FunctionTransformer(orig_employees_ds.merge)
    add_total_rows_transformer = AddTotalsRowTransformer()
    rewards_columns_transformer.set_next_step(multiply_by_10_transformer)
    multiply_by_10_transformer.set_next_step(merge_to_orig_ds_transformer)
    merge_to_orig_ds_transformer.set_next_step(add_total_rows_transformer)
    employees_pipeline = rewards_columns_transformer

    # Decorators chain pipeline: Option #3 using a Pipeline class (Live Demo)
    employees_pipeline = Pipeline(
        ColumnsSelectorTransformer(("salary", "bonus")),
        FunctionTransformer(lambda ds: ds * 10),
        FunctionTransformer(orig_employees_ds.merge),
        AddTotalsRowTransformer()
    )

    updated_employees_ds = employees_pipeline.transform(orig_employees_ds)

    print(updated_employees_ds)
