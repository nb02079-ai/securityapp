package securityapp.engine

/**
 * 알림 하나 = 메시지 하나.
 * 실제 앱은 상대방 메시지만 알림으로 받으므로 [isUser]는 평가용 재생에서만 true가 될 수 있다.
 * 메시지 내용은 어디에도 로그로 남기지 않는다 (plan.md 4.7.2).
 */
data class Message(
    val room: String,
    val sender: String,
    val text: String,
    val isUser: Boolean = false,
    /**
     * 단체방인지. 안드로이드 알림은 단체 대화 여부를 따로 알려 주므로(MessagingStyle.isGroupConversation) 앱에서는 그 값을 넣는다.
     * 모르면 null — 그때는 상대방 쪽 보낸 사람이 둘 이상이면 단체방으로 본다.
     */
    val isGroup: Boolean? = null,
)

/** 신호 분류 (docs/labeling/03_label_guide.md 2장) */
enum class Category { RELATION, DEMAND, PERSUASION, PROGRESS }

/** 기준표(v2.2)의 신호 17개. 코드는 라벨 파일·기준표와 같아야 한다. */
enum class Signal(val code: String, val label: String, val category: Category) {
    R1("R1", "단체방 맞장구", Category.RELATION),
    R2("R2", "친밀감 쌓기", Category.RELATION),
    D1("D1", "채널 이동 요구", Category.DEMAND),
    D2("D2", "투자금 입금 요구", Category.DEMAND),
    D3("D3", "대납·차용·선납 요구", Category.DEMAND),
    D4("D4", "지정 계좌·경로 통제", Category.DEMAND),
    D5("D5", "출금 조건부 추가 입금", Category.DEMAND),
    D6("D6", "비밀 유지·고립 요구", Category.DEMAND),
    D7("D7", "개인정보 요구·앱 설치", Category.DEMAND),
    P1("P1", "수익 보장·위험 부정", Category.PERSUASION),
    P2("P2", "권위·신분 과시", Category.PERSUASION),
    P3("P3", "긴급성·한정성 압박", Category.PERSUASION),
    P4("P4", "만남·확인 회피", Category.PERSUASION),
    G1("G1", "소액 선보상", Category.PROGRESS),
    G2("G2", "화제 급전환", Category.PROGRESS),
    G3("G3", "요구 금액 증가", Category.PROGRESS),
    G4("G4", "요구 반복", Category.PROGRESS);

    /** 돈 요구 (D2~D5). 경고 조건에 쓰임 (plan.md 4.2.3) */
    val isMoneyDemand: Boolean get() = this in setOf(D2, D3, D4, D5)

    /** 정상 대화에도 흔해 조합에 세지 않는 맥락 전용 신호 (plan.md 4.2.3의 5) */
    val isContextOnly: Boolean get() = this == R2

    companion object {
        fun fromCode(code: String): Signal? = entries.firstOrNull { it.code == code.trim().uppercase() }
    }
}

/** 대화방 위험 단계 (plan.md 4.2.1 ② 흐름 판정) */
enum class Level { OBSERVE, CAUTION, WARNING }

/** 감지된 신호 하나와 그 근거가 된 메시지 안의 구간 */
data class Detection(val signal: Signal, val evidence: IntRange)

/** 메시지 하나를 넣었을 때 엔진의 판단 */
data class Judgment(
    val room: String,
    val level: Level,
    val detections: List<Detection>,
    /** 이번 메시지로 단계가 올라갔으면 그 이유 (경고 화면의 설명에 쓰임) */
    val raisedBecause: String? = null,
)
