from enum import StrEnum
from typing import Dict, List, Optional, Type, Union

from data.models import LicitacaoV0, LicitacaoV1, LicitacaoV2, LicitacaoV3
from pydantic import BaseModel, field_validator

schema_version_to_extraction_model: Dict[
    int,
    Union[type[LicitacaoV0], type[LicitacaoV1], type[LicitacaoV2], type[LicitacaoV3]],
] = {0: LicitacaoV0, 1: LicitacaoV1, 2: LicitacaoV2, 3: LicitacaoV3}


class LLMModel(StrEnum):
    LLAMA3_70B = "llama3.3:70b"
    GEMMA3_27B = "gemma3:27b"
    QWEN2_5_70B = "qwen2.5:72b"
    DEEPSEEK_R1_70B = "deepseek-r1:70b"


class Shots(StrEnum):
    ZERO_SHOT = "zero_shot"
    ONE_SHOT = "one_shot"
    ONE_SHOT_OUT = "one_shot_out"
    FEW_SHOT = "few_shot"
    FEW_SHOT_OUT = "few_shot_out"
    DYNAMIC_ONE_SHOT = "dynamic_one_shot"
    DYNAMIC_ONE_SHOT_OUT = "dynamic_one_shot_out"
    SPECIFIC_ONE_SHOT = "specific_one_shot"
    SPECIFIC_ONE_SHOT_OUT = "specific_one_shot_out"
    SPECIFIC_FEW_SHOT = "specific_few_shot"
    SPECIFIC_FEW_SHOT_OUT = "specific_few_shot_out"
    CHAIN_OF_THOUGHT = "chain_of_thought"


class RagConfig(BaseModel):
    chunk_size: int
    overlap: int
    top_k: int


class ExperimentConfig(BaseModel):
    id: int
    extraction_model: Union[
        type[LicitacaoV0], type[LicitacaoV1], type[LicitacaoV2], type[LicitacaoV3]
    ]
    description: str
    prompt: str
    single_prompt: bool
    clean_context: bool
    shot: Shots
    rag_config: Optional[RagConfig]
    model: LLMModel


def load_configurations(experiments):
    configs = []
    ids = []
    descriptions = []
    for exp in experiments:
        if "rag_configuration" in exp:
            rag_config = RagConfig(
                chunk_size=exp["rag_configuration"]["chunk-size"],
                overlap=exp["rag_configuration"]["overlap"],
                top_k=exp["rag_configuration"]["top-k"],
            )
        else:
            rag_config = None

        configs.append(
            ExperimentConfig(
                id=exp["id"],
                extraction_model=schema_version_to_extraction_model[
                    exp["schema_version"]
                ],
                description=exp["description"],
                prompt=exp["prompt"],
                single_prompt=exp["single_prompt"],
                clean_context=exp["clean_context"],
                shot=exp.get("shot", "zero_shot"),
                rag_config=rag_config,
                model=exp["model"],
            )
        )
        ids.append(exp["id"])
        descriptions.append(exp["description"])

    if ids != list(range(len(experiments))):
        raise ValueError(
            f"Experiment IDs must be sequential starting from 0. Got: {ids}"
        )

    if len(set(descriptions)) != len(descriptions):
        raise ValueError("Experiment descriptions must be unique.")

    return configs
