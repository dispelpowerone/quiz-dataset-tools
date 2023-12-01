import copy
from driver_test_db.prebuild.stage import BaseStage, StageState


class PassthroughStage(BaseStage):
    def process(self, state: StageState) -> StageState:
        return copy.deepcopy(state)
