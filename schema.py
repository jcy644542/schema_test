from typing import List, Optional, Dict, Any, Annotated
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
import operator
from datetime import datetime

# 1. 에이전트 분석 결과 규격 (Audit Page UI와 일치)
# 각 에이전트(영수, 은진 등)가 작업 후 이 형식으로 결과를 보고합니다.
class AgentResult(BaseModel):
    agent_id: str = Field(..., description="에이전트명 (지혜, 영수, 은진, 은지, 차윤)")
    thought: str = Field(..., description="추론 과정 (CoT)")
    decision: str = Field(..., description="최종 의사결정 요약")
    status: str = Field(default="completed", description="상태: completed, warning, alert")
    confidence: float = Field(default=1.0)
    input_hash: str = Field(default="sha256-...")
    output_hash: str = Field(default="sha256-...")
    duration_ms: int = Field(default=0)
    citations: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 2. LangGraph 상태 정의 (사진 속 코드의 확장판)
class BatteryAgentState(TypedDict):
    """
    에이전트들이 공유하는 상태(State) 주머니입니다.
    """
    # 기본 정보
    batch_id: str
    supplier_id: str
    
    # 메시지 기록 (사진 속 messages와 동일)
    # Annotated와 operator.add를 사용하여 대화 내용이 누적됩니다.
    messages: Annotated[List[Dict[str, Any]], operator.add]
    
    # 감사 추적 데이터 (가장 중요!)
    # 모든 에이전트의 AgentResult가 여기에 쌓여 audit_page.tsx에 표시됩니다.
    audit_trail: Annotated[List[AgentResult], operator.add]
    
    # 에이전트별 전용 작업 공간 (중간 결과 보관)
    extracted_metadata: Dict[str, Any]  # 은진 에이전트가 추출한 값
    risk_analysis: Dict[str, Any]       # 영수/은지 에이전트가 분석한 값
    
    # 그래프 흐름 제어
    next_node: str                      # 지혜(Supervisor)가 결정하는 다음 에이전트
    requires_hitl: bool                 # 차윤(Controller)이 판단하는 인간 개입 여부
    is_finished: bool                   # 전체 프로세스 종료 플래그