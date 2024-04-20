import copy
from quiz_dataset_tools.prebuild.stage import BaseStage, StageState


class PassthroughStage(BaseStage):
    def process(self, state: StageState) -> StageState:
        return copy.deepcopy(state)
