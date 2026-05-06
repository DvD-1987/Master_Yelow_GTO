/**
 * GTO Poker Trainer - 主应用逻辑
 */

// 游戏数据（从JSON加载）
let SCENARIOS = null;

// 游戏状态
const gameState = {
    currentScenario: null,
    currentIndex: 0,
    shuffledScenarios: [],
    currentDifficulty: 'beginner',
    correctCount: 0,
    totalAttempts: 0,
    answered: false,
    gameStarted: false,
    sessionStats: {
        beginner: { correct: 0, total: 0 },
        intermediate: { correct: 0, total: 0 },
        advanced: { correct: 0, total: 0 }
    }
};

// 动作列表
const ACTIONS = ['fold', 'check', 'call', 'bet', 'raise'];

// Fisher-Yates 洗牌算法
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

/**
 * 初始化游戏
 */
function initGame() {
    loadSessionStats();
    
    // 加载游戏数据
    fetch('scenarios.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            SCENARIOS = data;
            console.log('游戏数据加载成功，共 ' + data.length + ' 个场景');
            // 数据加载完成后，初始化事件监听
            setupEventListeners();
        })
        .catch(error => {
            console.error('加载游戏数据失败:', error);
            alert('加载游戏数据失败，请检查 scenarios.json 是否存在。错误信息: ' + error.message);
        });
}

/**
 * 开始游戏（从封面进入）
 */
function startGame(difficulty) {
    console.log('startGame called with difficulty:', difficulty);
    try {
        // 验证数据加载
        if (!SCENARIOS || !Array.isArray(SCENARIOS)) {
            throw new Error('游戏数据未加载，请稍候再试。');
        }
        gameState.gameStarted = true;
        gameState.correctCount = 0;
        gameState.totalAttempts = 0;
        setDifficulty(difficulty || 'beginner');
        
        // 隐藏封面，显示游戏界面
        const cover = document.getElementById('coverScreen');
        const game = document.getElementById('gameScreen');
        if (!cover || !game) {
            throw new Error('DOM 元素缺失：coverScreen 或 gameScreen 未找到。');
        }
        cover.classList.add('hidden');
        game.classList.remove('hidden');
        console.log('Game started successfully');
    } catch (e) {
        console.error('Error in startGame:', e);
        alert('启动游戏时出错：' + e.message + '\n请检查控制台获取更多信息。');
    }
}

/**
 * 返回封面
 */
function goToCover() {
    gameState.gameStarted = false;
    document.getElementById('coverScreen').classList.remove('hidden');
    document.getElementById('gameScreen').classList.add('hidden');
}

/**
 * 设置难度并加载情境
 */
function setDifficulty(difficulty) {
    console.log('setDifficulty:', difficulty);
    if (!SCENARIOS || !Array.isArray(SCENARIOS)) {
        console.error('SCENARIOS not available');
        alert('游戏数据未加载，无法设置难度。');
        return;
    }
    gameState.currentDifficulty = difficulty;
    gameState.currentIndex = 0;
    gameState.answered = false;
    
    // 按难度筛选并洗牌
    let filtered;
    try {
        filtered = SCENARIOS.filter(s => s.difficulty === difficulty);
    } catch (e) {
        console.error('Error filtering scenarios:', e);
        alert('过滤情境时出错：' + e.message);
        return;
    }
    if (filtered.length === 0) {
        console.warn('No scenarios for difficulty:', difficulty);
        alert(`没有找到难度为 "${difficulty}" 的情境，请检查数据文件。`);
        return;
    }
    try {
        gameState.shuffledScenarios = shuffleArray(filtered);
    } catch (e) {
        console.error('Error shuffling scenarios:', e);
        alert('洗牌时出错：' + e.message);
        return;
    }
    
    // 更新UI
    updateDifficultyButtons();
    loadScenario(0);
    updateStats();
}

/**
 * 切换难度
 */
function switchDifficulty(difficulty) {
    if (!gameState.gameStarted) {
        startGame(difficulty);
    } else {
        setDifficulty(difficulty);
    }
}

/**
 * 加载情境
 */
function loadScenario(index) {
    if (index < 0 || index >= gameState.shuffledScenarios.length) return;
    
    gameState.currentIndex = index;
    gameState.currentScenario = gameState.shuffledScenarios[index];
    gameState.answered = false;
    
    renderScenario();
    renderContext();
    hideFeedback();
    enableActionButtons(true);
    updateProgress();
}

/**
 * 渲染情境
 */
function renderScenario() {
    const scenario = gameState.currentScenario;
    if (!scenario) return;
    
    // 手牌
    document.getElementById('playerCards').innerHTML = 
        scenario.hand.map(card => createCardHTML(card)).join('');
    // 显示位置
    document.getElementById('playerPosition').textContent = getPositionName(scenario.position);
    
    // 公共牌
    const boardEl = document.getElementById('boardCards');
    if (scenario.board && scenario.board.length > 0) {
        boardEl.innerHTML = scenario.board.map(card => createCardHTML(card)).join('');
    } else {
        boardEl.innerHTML = '<div class="no-board">翻前阶段，无公共牌</div>';
    }
    
    // 信息
    document.getElementById('potSize').textContent = `${scenario.potSize}bb`;
    document.getElementById('currentBet').textContent = scenario.currentBet > 0 ? `${scenario.currentBet}bb` : '-';
    document.getElementById('street').textContent = getStreetName(scenario.street);
    document.getElementById('effectiveStack').textContent = `${Math.round(scenario.effectiveStack / scenario.potSize)}bb`;
    document.getElementById('opponentAction').textContent = scenario.actionToPlayer || '首个行动';
    document.getElementById('potOdds').textContent = scenario.potOdds > 0 ? `${scenario.potOdds.toFixed(2)}:1` : '-';
    
    // 对手信息（手牌区域下方）
    const oppPosEl = document.getElementById('opponentPosition');
    const oppActionEl = document.getElementById('opponentActionInline');
    if (oppPosEl) oppPosEl.textContent = getPositionName(scenario.opponentPosition) || '-';
    if (oppActionEl) oppActionEl.textContent = scenario.actionToPlayer || '等待中';
}

/**
 * 渲染侧边栏
 */
function renderContext() {
    const scenario = gameState.currentScenario;
    if (!scenario) return;
    
    document.getElementById('ctx-street').textContent = getStreetName(scenario.street);
    document.getElementById('ctx-position').textContent = getPositionName(scenario.position);
    document.getElementById('ctx-pot').textContent = `${scenario.potSize}bb`;
    document.getElementById('ctx-stack').textContent = `${Math.round(scenario.effectiveStack / scenario.potSize)}bb`;
    document.getElementById('ctx-opponent').textContent = scenario.actionToPlayer || '首个行动';
    
    // 教学要点
    const teachingList = document.getElementById('teachingPoints');
    if (scenario.teaching && scenario.teaching.length > 0) {
        teachingList.innerHTML = scenario.teaching.map(t => `<li>${t}</li>`).join('');
    } else {
        teachingList.innerHTML = '<li>暂无教学要点</li>';
    }
    
    // 对手范围
    if (scenario.opponentRange) {
        document.getElementById('opponentValueRange').textContent = scenario.opponentRange.value || '-';
        document.getElementById('opponentBluffRange').textContent = scenario.opponentRange.bluff || '-';
    }
}

/**
 * 创建卡牌HTML
 */
function createCardHTML(card) {
    if (!card) return '';
    const isRed = card.includes('♥') || card.includes('♦');
    const colorClass = isRed ? 'red' : 'black';
    const rank = card.slice(0, -1);
    const suit = card.slice(-1);
    return `
        <div class="card ${colorClass}">
            <span class="card-corner top-left">${rank}${suit}</span>
            <span class="card-suit">${suit}</span>
            <span class="card-corner bottom-right">${rank}${suit}</span>
        </div>`;
}



/**
 * 执行动作
 */
function playerAction(action) {
    if (gameState.answered || !gameState.currentScenario) return;
    
    gameState.answered = true;
    gameState.totalAttempts++;
    
    const scenario = gameState.currentScenario;
    const result = evaluateAction(scenario, action);
    
    // 只有选择最优动作（最高频率）才算正确，计入统计
    if (result.isOptimal) gameState.correctCount++;
    
    const diff = gameState.currentDifficulty;
    gameState.sessionStats[diff].total++;
    if (result.isOptimal) gameState.sessionStats[diff].correct++;
    
    enableActionButtons(false);
    showFeedback(action, scenario, result);
    updateStats();
    saveSessionStats();
}

/**
 * 显示反馈
 */
function showFeedback(action, scenario, result) {
    const panel = document.getElementById('feedback');
    panel.classList.remove('correct', 'incorrect', 'suboptimal', 'show');
    panel.classList.add(result.feedbackType);
    
    document.getElementById('feedbackTitle').textContent = result.message.split('。')[0];
    
    const an = { fold: 'Fold', check: 'Check', call: 'Call', bet: 'Bet', raise: '3-Bet', '3bet': '3-Bet' };
    
    document.getElementById('feedbackContent').innerHTML = `
        <div class="feedback-row">
            <span class="feedback-label">你的选择：</span>
            <span class="feedback-value">${an[action] || action}</span>
        </div>
        <div class="feedback-row">
            <span class="feedback-label">GTO推荐：</span>
            <span class="feedback-value highlight">${an[scenario.optimalAction] || scenario.optimalAction}</span>
            <span class="feedback-freq">（${(scenario.actionFrequency * 100).toFixed(0)}%执行率）</span>
        </div>
        <div class="feedback-row">
            <span class="feedback-label">期望值：</span>
            <span class="feedback-value">${(scenario.ev * 100).toFixed(1)}bb</span>
        </div>`;
    
    let stats = '';
    if (scenario.mdf > 0) stats += `<div class="stat-item"><div class="stat-label">MDF</div><div class="stat-value">${scenario.mdf.toFixed(0)}%</div></div>`;
    if (scenario.potOdds > 0) stats += `<div class="stat-item"><div class="stat-label">底池赔率</div><div class="stat-value">${scenario.potOdds.toFixed(2)}:1</div></div>`;
    if (scenario.equity) stats += `<div class="stat-item"><div class="stat-label">胜率</div><div class="stat-value">${scenario.equity}</div></div>`;
    document.getElementById('feedbackStats').innerHTML = stats;
    
    // 显示推理
    document.getElementById('reasoningSection').classList.add('show');
    document.getElementById('reasoningText').innerHTML = formatReasoning(scenario);
    
    setTimeout(() => panel.classList.add('show'), 50);
}

/**
 * 格式化推理
 */
function formatReasoning(scenario) {
    let h = `<p class="explanation">${scenario.explanation}</p>`;
    h += `<div class="reasoning-detail">${scenario.reasoning.replace(/\n/g, '<br>')}</div>`;
    
    if (scenario.teaching && scenario.teaching.length) {
        h += `<div class="teaching-section"><strong>💡 教学要点：</strong><ul>`;
        scenario.teaching.forEach(t => { h += `<li>${t}</li>`; });
        h += `</ul></div>`;
    }
    if (scenario.commonMistakes && scenario.commonMistakes.length) {
        h += `<div class="mistakes-section"><strong>⚠️ 常见错误：</strong><ul>`;
        scenario.commonMistakes.forEach(m => { h += `<li>${m}</li>`; });
        h += `</ul></div>`;
    }
    return h;
}

/**
 * 更新统计
 */
function updateStats() {
    const acc = gameState.totalAttempts > 0 
        ? ((gameState.correctCount / gameState.totalAttempts) * 100).toFixed(1) : '0';
    document.getElementById('correctCount').textContent = gameState.correctCount;
    document.getElementById('totalScenarios').textContent = gameState.totalAttempts;
    document.getElementById('accuracy').textContent = `${acc}%`;
    document.getElementById('headerAccuracy').textContent = `${acc}%`;
}

/**
 * 更新进度
 */
function updateProgress() {
    const total = gameState.shuffledScenarios.length;
    const cur = gameState.currentIndex + 1;
    document.getElementById('progressFill').style.width = `${(cur / total) * 100}%`;
    document.getElementById('scenarioCounter').textContent = `${cur} / ${total}`;
    document.getElementById('headerProgress').textContent = `${cur}/${total}`;
}

/**
 * 更新难度按钮
 */
function updateDifficultyButtons() {
    document.querySelectorAll('.difficulty-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.difficulty === gameState.currentDifficulty);
    });
}

/**
 * 启用动作按钮
 */
function enableActionButtons(enabled) {
    ACTIONS.forEach(a => {
        const btn = document.getElementById(`btn-${a}`);
        if (btn) {
            btn.disabled = !enabled;
            btn.style.opacity = enabled ? '1' : '0.4';
            btn.style.pointerEvents = enabled ? 'auto' : 'none';
        }
    });
}

/**
 * 隐藏反馈
 */
function hideFeedback() {
    const fb = document.getElementById('feedback');
    fb.classList.remove('show', 'correct', 'incorrect');
    // Reset feedback content
    document.getElementById('feedbackTitle').textContent = '选择你的动作';
    document.getElementById('feedbackContent').innerHTML = '<p class="feedback-hint">根据情境信息，选择你认为的GTO最优动作</p>';
    document.getElementById('feedbackStats').innerHTML = '';
    // Reset reasoning - 只清空内容，不删除元素结构
    const reasoningText = document.getElementById('reasoningText');
    if (reasoningText) {
        reasoningText.innerHTML = '<p class="reasoning-hint">答题后显示详细分析</p>';
    }
    const reasoningSection = document.getElementById('reasoningSection');
    reasoningSection?.classList.remove('show');
}

/**
 * 上一题
 */
function previousScenario() {
    if (gameState.currentIndex > 0) loadScenario(gameState.currentIndex - 1);
}

/**
 * 下一题
 */
function nextScenario() {
    if (gameState.currentIndex < gameState.shuffledScenarios.length - 1) {
        loadScenario(gameState.currentIndex + 1);
    } else {
        // 重新洗牌
        setDifficulty(gameState.currentDifficulty);
    }
}

/**
 * 设置事件监听
 */
function setupEventListeners() {
    // 难度按钮
    document.querySelectorAll('.difficulty-btn').forEach(btn => {
        btn.addEventListener('click', () => switchDifficulty(btn.dataset.difficulty));
    });
    
    // 动作按钮 - 用事件委托
    ACTIONS.forEach(action => {
        const btn = document.getElementById(`btn-${action}`);
        if (btn) {
            btn.addEventListener('click', () => playerAction(action));
        }
    });
    
    // 导航按钮
    document.querySelector('.nav-btn.prev')?.addEventListener('click', previousScenario);
    document.querySelector('.nav-btn.next')?.addEventListener('click', nextScenario);
    
    // 键盘快捷键
    document.addEventListener('keydown', e => {
        if (!gameState.gameStarted) return;
        if (gameState.answered) {
            if (e.key === 'ArrowRight') nextScenario();
            if (e.key === 'ArrowLeft') previousScenario();
            return;
        }
        const map = { f: 'fold', c: 'check', l: 'call', b: 'bet', r: 'raise' };
        const a = map[e.key.toLowerCase()];
        if (a) playerAction(a);
    });
}

/**
 * 保存/加载
 */
function saveSessionStats() {
    try { sessionStorage.setItem('gto-poker-stats', JSON.stringify(gameState.sessionStats)); } 
    catch (e) {}
}

function loadSessionStats() {
    try {
        const s = sessionStorage.getItem('gto-poker-stats');
        if (s) gameState.sessionStats = JSON.parse(s);
    } catch (e) {}
}

// 启动 - 修复：确保在 DOM 已加载时执行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGame);
} else {
    initGame();
}

/**
 * 评估动作：支持混合策略判定
 * 返回：{ isOptimal, isSuboptimal, isWrong, frequency, feedbackType }
 * feedbackType: 'correct' | 'suboptimal' | 'wrong'
 */
function evaluateAction(scenario, playerAction) {
    // 基础：当前只存了一个optimalAction + actionFrequency
    // 未来可扩展为 actions: [{action, freq}, ...]
    
    const optimal = scenario.optimalAction;
    const freq = scenario.actionFrequency || 1.0;
    
    // 判断玩家动作
    if (playerAction === optimal) {
        // 选择了最优动作
        if (freq >= 0.5) {
            return {
                isOptimal: true,
                isSuboptimal: false,
                isWrong: false,
                frequency: freq,
                feedbackType: 'correct',
                message: `✅ 正确！这是GTO最优动作（执行率${(freq*100).toFixed(0)}%）`
            };
        } else {
            // 频率低于50%，但仍是最高频动作（混合策略中的次选）
            return {
                isOptimal: true, // 仍算"正确"，但提示是次选
                isSuboptimal: true,
                isWrong: false,
                frequency: freq,
                feedbackType: 'suboptimal',
                message: `⚠️ 次优选择。${getActionName(optimal)}是GTO动作之一（执行率${(freq*100).toFixed(0)}%），但存在更高频率的动作。`
            };
        }
    } else {
        // 选择了错误动作
        return {
            isOptimal: false,
            isSuboptimal: false,
            isWrong: true,
            frequency: freq,
            feedbackType: 'wrong',
            message: `❌ 错误。GTO推荐：${getActionName(optimal)}（执行率${(freq*100).toFixed(0)}%）`
        };
    }
}

function getActionName(action) {
    const names = { fold: '弃牌', check: '过牌', call: '跟注', bet: '下注', raise: '加注', '3bet': '3-Bet' };
    return names[action] || action;
}

/**
 * 辅助函数：获取阶段名称
 */
function getStreetName(street) {
    const names = { preflop: '翻前', flop: '翻牌圈', turn: '转牌圈', river: '河牌圈' };
    return names[street] || street;
}

/**
 * 辅助函数：获取位置名称
 */
function getPositionName(pos) {
    const names = {
        UTG: '枪口位', 'UTG+1': '枪口+1', 
        MP: '中位', 'MP+1': '中位+1',
        HJ: '劫持位', CO: '拦截位', BTN: '庄位', 
        SB: '小盲位', BB: '大盲位'
    };
    // IP/OP 是位置优势术语，不是位置名，返回原始值或空
    if (pos === 'IP' || pos === 'OOP') return '';
    return names[pos] || pos || '';
}

/**
 * 弹窗提示（即将上线）
 */
function showComingSoon(feature) {
    const modal = document.getElementById('comingSoonModal');
    document.getElementById('modalTitle').textContent = feature;
    modal.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('comingSoonModal').classList.add('hidden');
}
/**
 * 概率计算模块
 */
function openProbabilityModal() {
    document.getElementById('probabilityModal').classList.remove('hidden');
    // 默认显示第一个tab
    switchProbTab('basic');
}

function closeProbabilityModal() {
    document.getElementById('probabilityModal').classList.add('hidden');
}

function switchProbTab(tab) {
    // 切换tab按钮状态：不能依赖全局 event，openProbabilityModal() 主动调用时没有 event
    document.querySelectorAll('.prob-tab').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes("'" + tab + "'")) {
            btn.classList.add('active');
        }
    });
    
    // 切换内容显示
    document.querySelectorAll('.prob-content').forEach(content => content.classList.remove('active'));
    const target = document.getElementById('prob-' + tab);
    if (target) target.classList.add('active');
}

/**
 * 简单胜率计算（基于预定义数据）
 */
function calcSimple() {
    const hand = document.getElementById('calcHand').value.trim().toUpperCase();
    const range = document.getElementById('calcRange').value;
    
    // 预定义胜率数据（简化版）
    const equityMap = {
        'AA': 0.85, 'KK': 0.82, 'QQ': 0.80, 'JJ': 0.77, 'TT': 0.75,
        'AKS': 0.65, 'AQS': 0.64, 'AJS': 0.63, 'AKO': 0.60, 'AQO': 0.58,
        'T9S': 0.55, '987': 0.45, '22': 0.50
    };
    
    const defaultEquity = 0.50;
    const equity = equityMap[hand] || defaultEquity;
    
    // 根据对手范围调整
    let rangeMultiplier = 1.0;
    if (range === 'top20') rangeMultiplier = 0.85;
    else if (range === 'top10') rangeMultiplier = 0.75;
    else if (range === 'pair+') rangeMultiplier = 0.70;
    
    const finalEquity = Math.min(equity * rangeMultiplier, 0.95);
    
    // 显示结果
    document.getElementById('resultEquity').textContent = (finalEquity * 100).toFixed(1) + '%';
    document.getElementById('resultPercent').textContent = (finalEquity * 100).toFixed(1) + '%';
    document.getElementById('calcResult').classList.remove('hidden');
}

/**
 * 高级胜率计算（简化版）
 */
function calcAdvanced() {
    // 简化实现：返回随机值（实际应使用pokersolver等库）
    const equity1 = (Math.random() * 0.4 + 0.3).toFixed(3);
    const equity2 = (Math.random() * 0.4 + 0.3).toFixed(3);
    const tie = (1 - parseFloat(equity1) - parseFloat(equity2)).toFixed(3);
    
    document.getElementById('proEquity1').textContent = (equity1 * 100).toFixed(1) + '%';
    document.getElementById('proEquity2').textContent = (equity2 * 100).toFixed(1) + '%';
    document.getElementById('proTie').textContent = (Math.max(0, tie) * 100).toFixed(1) + '%';
    document.getElementById('proResult').classList.remove('hidden');
}

/**
 * MDF计算
 */
function calcMDF() {
    const pot = parseFloat(document.getElementById('mdfPot').value) || 100;
    const bet = parseFloat(document.getElementById('mdfBet').value) || 50;
    
    const mdf = pot / (pot + bet);
    const freq = (mdf * 100).toFixed(1);
    
    document.getElementById('mdfValue').textContent = mdf.toFixed(3);
    document.getElementById('mdfFreq').textContent = freq + '%';
    document.getElementById('mdfResult').classList.remove('hidden');
}

/**
 * 复盘模式
 */
let reviewData = {
    preflop: { hand: null, position: null, action: null, equity: null },
    flop: { board: null, pot: null, bet: null, action: null, equity: null, odds: null },
    turn: { card: null, pot: null, bet: null, action: null, equity: null, odds: null },
    river: { card: null, pot: null, bet: null, action: null, equity: null, odds: null }
};

function openReviewModal() {
    document.getElementById('reviewModal').classList.remove('hidden');
    resetReviewSteps();
}

function closeReviewModal() {
    document.getElementById('reviewModal').classList.add('hidden');
}

function resetReviewSteps() {
    document.querySelectorAll('.review-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.review-steps .step').forEach(el => el.classList.remove('active'));
    document.getElementById('review-preflop').classList.add('active');
    document.getElementById('step-preflop').classList.add('active');
    reviewData = {
        preflop: { hand: null, position: null, action: null, equity: null },
        flop: { board: null, pot: null, bet: null, action: null, equity: null, odds: null },
        turn: { card: null, pot: null, bet: null, action: null, equity: null, odds: null },
        river: { card: null, pot: null, bet: null, action: null, equity: null, odds: null }
    };
}

function nextReviewStep(step) {
    document.querySelectorAll('.review-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.review-steps .step').forEach(el => el.classList.remove('active'));
    document.getElementById('review-' + step).classList.add('active');
    document.getElementById('step-' + step).classList.add('active');
}

function prevReviewStep(step) {
    nextReviewStep(step);
}

/**
 * 翻前分析
 */
function analyzePreflop() {
    const hand = document.getElementById('revPreflopHand').value.trim();
    const pos = document.getElementById('revPreflopPos').value;
    const action = document.getElementById('revPreflopAction').value;
    
    // 简化胜率计算
    let equity = 0.50;
    if (hand.includes('A') && hand.includes('A')) equity = 0.85; // AA
    else if (hand.includes('A')) equity = 0.65; // AK, AQ etc
    else if (hand.match(/[KQJ]/)) equity = 0.60;
    else equity = 0.50;
    
    // 根据位置调整
    const posFactor = { 'UTG': 0.9, 'UTG+1': 0.9, 'MP': 0.95, 'MP+1': 0.95, 'HJ': 1.0, 'CO': 1.05, 'BTN': 1.1, 'SB': 0.95, 'BB': 1.0 };
    equity = Math.min(equity * (posFactor[pos] || 1.0), 0.95);
    
    reviewData.preflop = { hand, position: pos, action, equity };
    
    // 显示结果
    document.getElementById('revPreflopEquity').textContent = (equity * 100).toFixed(1) + '%';
    const advice = action === 'raise' ? '建议加注（符合GTO）' : 
                  action === 'fold' ? '建议弃牌（弱牌）' : '建议跟注（中等牌）';
    document.getElementById('revPreflopAdvice').textContent = advice;
    document.getElementById('revPreflopResult').classList.remove('hidden');
}

/**
 * 翻牌分析
 */
function analyzeFlop() {
    const board = document.getElementById('revFlopBoard').value.trim();
    const pot = parseFloat(document.getElementById('revFlopPot').value) || 100;
    const bet = parseFloat(document.getElementById('revFlopBet').value) || 0;
    const action = document.getElementById('revFlopAction').value;
    
    // 简化胜率：随机值（实际应计算）
    const equity = 0.5 + Math.random() * 0.3;
    const odds = bet > 0 ? (pot / (pot + bet)).toFixed(3) : '-';
    
    reviewData.flop = { board, pot, bet, action, equity, odds };
    
    document.getElementById('revFlopEquity').textContent = (equity * 100).toFixed(1) + '%';
    document.getElementById('revFlopOdds').textContent = odds;
    document.getElementById('revFlopAdvice').textContent = action === 'bet' ? '建议下注' : 
                                                     action === 'check' ? '建议过牌' : 
                                                     action === 'call' ? '建议跟注' : '建议弃牌';
    document.getElementById('revFlopResult').classList.remove('hidden');
}

/**
 * 转牌分析
 */
function analyzeTurn() {
    const card = document.getElementById('revTurnCard').value.trim();
    const pot = parseFloat(document.getElementById('revTurnPot').value) || 200;
    const bet = parseFloat(document.getElementById('revTurnBet').value) || 0;
    const action = document.getElementById('revTurnAction').value;
    
    const equity = 0.5 + Math.random() * 0.3;
    const odds = bet > 0 ? (pot / (pot + bet)).toFixed(3) : '-';
    
    reviewData.turn = { card, pot, bet, action, equity, odds };
    
    document.getElementById('revTurnEquity').textContent = (equity * 100).toFixed(1) + '%';
    document.getElementById('revTurnOdds').textContent = odds;
    document.getElementById('revTurnAdvice').textContent = action === 'bet' ? '建议下注' : 
                                                    action === 'check' ? '建议过牌' : 
                                                    action === 'call' ? '建议跟注' : '建议弃牌';
    document.getElementById('revTurnResult').classList.remove('hidden');
}

/**
 * 河牌分析
 */
function analyzeRiver() {
    const card = document.getElementById('revRiverCard').value.trim();
    const pot = parseFloat(document.getElementById('revRiverPot').value) || 400;
    const bet = parseFloat(document.getElementById('revRiverBet').value) || 0;
    const action = document.getElementById('revRiverAction').value;
    
    const equity = 0.5 + Math.random() * 0.3;
    const odds = bet > 0 ? (pot / (pot + bet)).toFixed(3) : '-';
    
    reviewData.river = { card, pot, bet, action, equity, odds };
    
    document.getElementById('revRiverEquity').textContent = (equity * 100).toFixed(1) + '%';
    document.getElementById('revRiverOdds').textContent = odds;
    document.getElementById('revRiverAdvice').textContent = action === 'bet' ? '建议下注' : 
                                                     action === 'check' ? '建议过牌' : 
                                                     action === 'call' ? '建议跟注' : '建议弃牌';
    document.getElementById('revRiverResult').classList.remove('hidden');
}

/**
 * 保存复盘到题库
 */
function saveReview() {
    const complexity = parseInt(document.getElementById('revComplexity').value) || 5;
    
    // 确定难度
    let difficulty = 'intermediate';
    if (complexity <= 3) difficulty = 'beginner';
    else if (complexity >= 7) difficulty = 'advanced';
    
    // 生成题目
    const scenario = {
        id: Date.now(), // 临时ID，后续会重新编号
        difficulty: difficulty,
        street: 'preflop', // 默认为翻前，实际应根据复盘内容确定
        position: reviewData.preflop.position || 'BTN',
        tableSize: 9,
        hand: reviewData.preflop.hand ? reviewData.preflop.hand.split(' ') : ['A♠', 'A♥'],
        board: reviewData.flop.board ? reviewData.flop.board.split(' ') : [],
        potSize: reviewData.flop.pot || 100,
        effectiveStack: 100,
        currentBet: reviewData.flop.bet || 0,
        actionToPlayer: '',
        optimalAction: reviewData.preflop.action || 'raise',
        actionFrequency: 1.0,
        ev: 0.5,
        potOdds: reviewData.flop.odds || 0,
        mdf: 0,
        explanation: `复盘收录：翻前${reviewData.preflop.position}位置，${reviewData.preflop.hand}，行动${reviewData.preflop.action}`,
        reasoning: `复盘模式生成题目。翻前${reviewData.preflop.position}位置，手牌${reviewData.preflop.hand}，选择${reviewData.preflop.action}。复盘评分${complexity}分。`,
        equity: (reviewData.preflop.equity * 100).toFixed(0) + '%',
        opponentRange: { value: null, bluff: null },
        teaching: ['复盘收录', `复杂度${complexity}分`],
        commonMistakes: ['复盘生成'],
        tags: ['review', '复盘', difficulty],
        complexity: complexity,
        source: 'review' // 标记来源为复盘
    };
    
    // 保存到localStorage（模拟，实际应写入scenarios.json）
    const reviews = JSON.parse(localStorage.getItem('reviews') || '[]');
    reviews.push(scenario);
    localStorage.setItem('reviews', JSON.stringify(reviews));
    
    alert('复盘题目已保存！总数：' + reviews.length + '道（复盘模式收录）');
    resetReview();
}
