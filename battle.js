/**
 * GTO Poker - 对战模式逻辑 (版本 20260505)
 * 6人桌：1玩家 + 5个AI
 * 每人100BB起始筹码
 */

console.log('✅ battle.js已加载 - 版本 20260505');

// ==================== 对战模式状态（全局）====================
var battleState = {
    active: false,
    players: [],      // 6个玩家对象
    deck: [],         // 牌组
    board: [],        // 公共牌
    pot: 0,          // 底池
    currentBet: 0,    // 当前下注额
    currentStreet: 'preflop', // 当前阶段
    currentPlayerIndex: 0, // 当前行动玩家索引
    dealerIndex: 0,      // 庄家位置
    playerSeatIndex: 0,   // 玩家座位（固定为0，即BTN位置）
    gameOver: false
};

// 座位位置名称（6人桌）
var SEAT_POSITIONS = ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO'];

// ==================== 初始化对战 ====================
function initBattle() {
    console.log('[对战] 初始化对战模式...');
    battleState.active = true;
    battleState.pot = 0;
    battleState.currentBet = 0;
    battleState.currentStreet = 'preflop';
    battleState.board = [];
    battleState.gameOver = false;
    battleState.players = [];
    
    // 创建6个玩家（0=玩家，1-5=AI）
    for (var i = 0; i < 6; i++) {
        battleState.players.push({
            seatIndex: i,
            position: SEAT_POSITIONS[i],
            isHuman: i === battleState.playerSeatIndex,
            name: i === battleState.playerSeatIndex ? '你' : 'AI ' + (i + 1),
            chips: 10000, // 100BB = 10000（1BB=100）
            hand: [],
            isFolded: false,
            isAllIn: false,
            currentBet: 0,
            totalBetThisHand: 0
        });
    }
    
    // 设置庄家（BTN位置）
    battleState.dealerIndex = battleState.playerSeatIndex;
    // preflop从UTG（座位3）开始行动
    battleState.currentPlayerIndex = (battleState.dealerIndex + 3) % 6;
    
    // 初始化牌组并洗牌
    initDeck();
    
    // 发牌
    dealCards();
    
    // 收取盲注
    postBlinds();
    
    // 更新UI
    updateBattleUI();
    
    console.log('[对战] 初始化完成，玩家座位：', battleState.playerSeatIndex);
    
    // 启动游戏循环 - 直接开始UTG的行动
    var firstPlayer = battleState.players[battleState.currentPlayerIndex];
    if (firstPlayer && !firstPlayer.isHuman) {
        setTimeout(function() { aiAction(battleState.currentPlayerIndex); }, 1000);
    }
}

// 初始化牌组
function initDeck() {
    var suits = ['♠', '♥', '♦', '♣'];
    var ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
    battleState.deck = [];
    
    for (var s = 0; s < suits.length; s++) {
        for (var r = 0; r < ranks.length; r++) {
            battleState.deck.push(ranks[r] + suits[s]);
        }
    }
    
    // 洗牌
    battleState.deck = shuffleArray(battleState.deck);
    console.log('[对战] 牌组初始化完成，共', battleState.deck.length, '张牌');
}

// 洗牌算法
function shuffleArray(array) {
    var shuffled = array.slice();
    for (var i = shuffled.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = shuffled[i];
        shuffled[i] = shuffled[j];
        shuffled[j] = temp;
    }
    return shuffled;
}

// 发牌（每人2张底牌）
function dealCards() {
    for (var p = 0; p < battleState.players.length; p++) {
        var player = battleState.players[p];
        player.hand = [battleState.deck.pop(), battleState.deck.pop()];
        player.isFolded = false;
        player.isAllIn = false;
        player.currentBet = 0;
        player.totalBetThisHand = 0;
    }
    console.log('[对战] 发牌完成');
}

// 收取盲注
function postBlinds() {
    var sbIndex = (battleState.dealerIndex + 1) % 6;
    var bbIndex = (battleState.dealerIndex + 2) % 6;
    
    // 小盲 0.5BB = 50
    battleState.players[sbIndex].chips -= 50;
    battleState.players[sbIndex].currentBet = 50;
    battleState.players[sbIndex].totalBetThisHand = 50;
    
    // 大盲 1BB = 100
    battleState.players[bbIndex].chips -= 100;
    battleState.players[bbIndex].currentBet = 100;
    battleState.players[bbIndex].totalBetThisHand = 100;
    
    battleState.pot = 150; // 50 + 100
    battleState.currentBet = 100; // 大盲设为当前下注
    
    console.log('[对战] 盲注已收取：SB 50, BB 100, 底池 150');
}

// ==================== UI更新 ====================
function updateBattleUI() {
    updateSeatsDisplay();
    updatePlayerHand();
    updateBoardDisplay();
    updateInfoBar();
    updateActionButtons();
}

function updateSeatsDisplay() {
    // 移除现有座位
    var oldSeats = document.querySelectorAll('.seat');
    for (var i = 0; i < oldSeats.length; i++) {
        oldSeats[i].parentNode.removeChild(oldSeats[i]);
    }
    
    var tableFelt = document.querySelector('.table-felt');
    if (!tableFelt) {
        console.error('[对战] 找不到.table-felt元素');
        return;
    }
    
    // 创建6个座位
    for (var j = 0; j < battleState.players.length; j++) {
        var player = battleState.players[j];
        var seat = document.createElement('div');
        var className = 'seat';
        if (player.isFolded) className += ' folded';
        if (j === battleState.playerSeatIndex) className += ' player-seat';
        if (j === battleState.currentPlayerIndex && !player.isFolded) className += ' active';
        
        seat.className = className;
        seat.setAttribute('data-position', player.position);
        
        seat.innerHTML = '<div class="seat-name">' + player.name + '</div>' +
                       '<div class="seat-chips">' + (player.chips / 100).toFixed(1) + 'bb</div>' +
                       (player.isFolded ? '<div class="seat-status">已弃牌</div>' : '') +
                       (player.isAllIn ? '<div class="seat-status">ALL IN</div>' : '');
        
        tableFelt.appendChild(seat);
    }
}

function updatePlayerHand() {
    var player = battleState.players[battleState.playerSeatIndex];
    if (player && player.hand.length === 2) {
        var playerCardsEl = document.getElementById('playerCards');
        if (playerCardsEl) {
            playerCardsEl.innerHTML = createCardHTML(player.hand[0]) + createCardHTML(player.hand[1]);
        }
    }
}

function createCardHTML(card) {
    if (!card) return '';
    var isRed = card.indexOf('♥') >= 0 || card.indexOf('♦') >= 0;
    var colorClass = isRed ? 'red' : 'black';
    var rank = card.substring(0, card.length - 1);
    var suit = card.substring(card.length - 1);
    return '<div class="card ' + colorClass + '">' +
           '<span class="card-corner top-left">' + rank + suit + '</span>' +
           '<span class="card-suit">' + suit + '</span>' +
           '<span class="card-corner bottom-right">' + rank + suit + '</span>' +
           '</div>';
}

function updateBoardDisplay() {
    var boardEl = document.getElementById('boardCards');
    if (!boardEl) return;
    
    if (battleState.board.length > 0) {
        var html = '';
        for (var k = 0; k < battleState.board.length; k++) {
            html += createCardHTML(battleState.board[k]);
        }
        boardEl.innerHTML = html;
    } else {
        boardEl.innerHTML = '<div class="no-board">翻前阶段，无公共牌</div>';
    }
}

function updateInfoBar() {
    var player = battleState.players[battleState.playerSeatIndex];
    var currentPlayer = battleState.players[battleState.currentPlayerIndex];
    
    var potSizeEl = document.getElementById('potSize');
    if (potSizeEl) potSizeEl.textContent = (battleState.pot / 100).toFixed(1) + 'bb';
    
    var currentBetEl = document.getElementById('currentBet');
    if (currentBetEl) currentBetEl.textContent = battleState.currentBet > 0 ? 
        (battleState.currentBet / 100).toFixed(1) + 'bb' : '-';
    
    var streetEl = document.getElementById('street');
    if (streetEl) streetEl.textContent = getStreetNameChinese(battleState.currentStreet);
    
    var effectiveStackEl = document.getElementById('effectiveStack');
    if (effectiveStackEl && player) effectiveStackEl.textContent = (player.chips / 100).toFixed(1) + 'bb';
    
    // 显示当前回合玩家
    var turnIndicator = document.getElementById('turnIndicator');
    if (!turnIndicator) {
        turnIndicator = document.createElement('div');
        turnIndicator.id = 'turnIndicator';
        turnIndicator.style.cssText = 'text-align:center;font-size:18px;font-weight:bold;margin:10px 0;padding:8px;background:#1a1a2e;border-radius:8px;color:#e94560;';
        var tableFelt = document.querySelector('.table-felt');
        if (tableFelt && tableFelt.parentNode) {
            tableFelt.parentNode.insertBefore(turnIndicator, tableFelt);
        }
    }
    if (currentPlayer) {
        var isPlayerTurn = battleState.currentPlayerIndex === battleState.playerSeatIndex;
        turnIndicator.textContent = isPlayerTurn ? '🎯 轮到你了！' : '⏳ 等待 ' + currentPlayer.name + ' (' + currentPlayer.position + ') 行动...';
        turnIndicator.style.color = isPlayerTurn ? '#00ff88' : '#e94560';
    }
}

function updateActionButtons() {
    var isPlayerTurn = battleState.currentPlayerIndex === battleState.playerSeatIndex;
    var player = battleState.players[battleState.playerSeatIndex];
    
    var disabled = !isPlayerTurn || player.isFolded || player.isAllIn || battleState.gameOver;
    
    var btnFold = document.getElementById('btn-fold');
    var btnCheck = document.getElementById('btn-check');
    var btnCall = document.getElementById('btn-call');
    var btnBet = document.getElementById('btn-bet');
    var btnRaise = document.getElementById('btn-raise');
    var btnAllin = document.getElementById('btn-allin');
    
    if (btnFold) btnFold.disabled = disabled;
    if (btnCheck) btnCheck.disabled = disabled || battleState.currentBet > player.currentBet;
    if (btnCall) btnCall.disabled = disabled || battleState.currentBet <= player.currentBet;
    if (btnBet) btnBet.disabled = disabled;
    if (btnRaise) btnRaise.disabled = disabled;
    if (btnAllin) btnAllin.disabled = disabled;
}

function getStreetNameChinese(street) {
    var names = {
        'preflop': '翻前',
        'flop': '翻牌',
        'turn': '转牌',
        'river': '河牌',
        'showdown': '摊牌'
    };
    return names[street] || street;
}

// ==================== 动作处理 ====================
function handlePlayerAction(action) {
    var player = battleState.players[battleState.playerSeatIndex];
    if (!player || player.isFolded || player.isAllIn) return;
    
    console.log('[对战] 玩家执行动作:', action);
    
    switch(action) {
        case 'fold':
            player.isFolded = true;
            console.log('[对战] 玩家弃牌');
            break;
        case 'check':
            if (battleState.currentBet > player.currentBet) {
                console.log('[对战] 不能check，需要跟注');
                return;
            }
            console.log('[对战] 玩家check');
            break;
        case 'call':
            var callAmount = battleState.currentBet - player.currentBet;
            if (callAmount > 0) {
                var actualCall = Math.min(callAmount, player.chips);
                player.chips -= actualCall;
                player.currentBet += actualCall;
                player.totalBetThisHand += actualCall;
                battleState.pot += actualCall;
                
                if (player.chips === 0) player.isAllIn = true;
            }
            console.log('[对战] 玩家跟注', callAmount);
            break;
        case 'bet':
        case 'raise':
            var betAmount = battleState.currentBet > 0 ? battleState.currentBet * 2 : 200;
            var actualBet = Math.min(betAmount, player.chips + player.currentBet);
            var additional = actualBet - player.currentBet;
            
            if (additional > 0) {
                player.chips -= additional;
                player.currentBet = actualBet;
                player.totalBetThisHand += additional;
                battleState.pot += additional;
                battleState.currentBet = actualBet;
                
                if (player.chips === 0) player.isAllIn = true;
            }
            console.log('[对战] 玩家下注/加注', additional);
            break;
        case 'allin':
            var allinAmount = player.chips;
            player.chips = 0;
            player.currentBet += allinAmount;
            player.totalBetThisHand += allinAmount;
            battleState.pot += allinAmount;
            battleState.currentBet = Math.max(battleState.currentBet, player.currentBet);
            player.isAllIn = true;
            console.log('[对战] 玩家ALL IN', allinAmount);
            break;
    }
    
    // 检查游戏是否结束
    checkBattleEnd();
    
    // 移动到下一个玩家
    if (!battleState.gameOver) {
        moveToNextPlayer();
    }
}

function moveToNextPlayer() {
    // 记录当前起始玩家（用于检测一轮是否结束）
    var startPlayerIndex = battleState.currentPlayerIndex;
    var nextIndex = (battleState.currentPlayerIndex + 1) % 6;
    var loops = 0;
    var foundNext = false;
    
    // 找到下一个未弃牌且未ALL IN的玩家
    while (loops < 6) {
        var nextPlayer = battleState.players[nextIndex];
        if (!nextPlayer.isFolded && !nextPlayer.isAllIn) {
            // 检查是否回到了起始点（一轮结束）
            if (nextIndex === startPlayerIndex) {
                // 一轮结束，进入下一阶段
                nextStreet();
                return;
            }
            battleState.currentPlayerIndex = nextIndex;
            foundNext = true;
            
            // 如果是AI，执行AI动作
            if (!nextPlayer.isHuman) {
                setTimeout(function() { aiAction(nextIndex); }, 1000);
            }
            break;
        }
        nextIndex = (nextIndex + 1) % 6;
        loops++;
    }
    
    // 如果没找到下一个玩家（可能所有人都弃牌或ALL IN）
    if (!foundNext) {
        // 检查游戏是否结束
        checkBattleEnd();
        if (!battleState.gameOver) {
            // 进入下一阶段
            nextStreet();
        }
        return;
    }
    
    updateBattleUI();
}

// 检查一轮是否真的结束（防止无限循环）
function isRoundComplete() {
    // 如果所有未弃牌玩家都下注到相同金额，返回true
    var activePlayers = 0;
    var allMatched = true;
    for (var i = 0; i < battleState.players.length; i++) {
        var p = battleState.players[i];
        if (!p.isFolded) {
            activePlayers++;
            if (p.currentBet !== battleState.currentBet && !p.isAllIn) {
                allMatched = false;
            }
        }
    }
    return activePlayers <= 1 || allMatched;
}

// 进入下一阶段
function nextStreet() {
    console.log('[对战] 进入下一阶段，当前：', battleState.currentStreet);
    
    // 重置所有玩家的下注额
    for (var i = 0; i < battleState.players.length; i++) {
        battleState.players[i].currentBet = 0;
    }
    battleState.currentBet = 0;
    
    // 根据当前阶段发牌
    switch(battleState.currentStreet) {
        case 'preflop':
            // 发flop（3张）
            battleState.board = [battleState.deck.pop(), battleState.deck.pop(), battleState.deck.pop()];
            battleState.currentStreet = 'flop';
            console.log('[对战] Flop:', battleState.board);
            break;
        case 'flop':
            // 发turn（1张）
            battleState.board.push(battleState.deck.pop());
            battleState.currentStreet = 'turn';
            console.log('[对战] Turn:', battleState.board);
            break;
        case 'turn':
            // 发river（1张）
            battleState.board.push(battleState.deck.pop());
            battleState.currentStreet = 'river';
            console.log('[对战] River:', battleState.board);
            break;
        case 'river':
            // 进入摊牌
            battleState.currentStreet = 'showdown';
            console.log('[对战] 进入摊牌阶段');
            showdown();
            return;
    }
    
    // 设置下一个行动玩家（从小盲开始）
    battleState.currentPlayerIndex = (battleState.dealerIndex + 1) % 6;
    
    // 如果下一个玩家已弃牌或ALL IN，继续找下一个
    var loops = 0;
    while (loops < 6) {
        var p = battleState.players[battleState.currentPlayerIndex];
        if (!p.isFolded && !p.isAllIn) {
            break;
        }
        battleState.currentPlayerIndex = (battleState.currentPlayerIndex + 1) % 6;
        loops++;
    }
    
    updateBattleUI();
    
    // 如果下一个是AI，自动行动
    var nextPlayer = battleState.players[battleState.currentPlayerIndex];
    if (nextPlayer && !nextPlayer.isHuman && !nextPlayer.isFolded && !nextPlayer.isAllIn) {
        setTimeout(function() { aiAction(battleState.currentPlayerIndex); }, 1000);
    }
}

// 摊牌阶段
function showdown() {
    console.log('[对战] 摊牌阶段 - 简化版，直接结束');
    // 简化：暂时直接结束游戏
    battleState.gameOver = true;
    var player = battleState.players[battleState.playerSeatIndex];
    var activePlayers = 0;
    for (var i = 0; i < battleState.players.length; i++) {
        if (!battleState.players[i].isFolded) activePlayers++;
    }
    showBattleResult(activePlayers === 1 && !player.isFolded);
}

function aiAction(playerIndex) {
    var player = battleState.players[playerIndex];
    if (!player || player.isFolded || player.isAllIn) return;
    
    // 根据情况选择动作
    var action;
    var callAmount = battleState.currentBet - player.currentBet;
    var potOdds = callAmount > 0 ? callAmount / (battleState.pot + callAmount) : 0;
    
    // 简单策略：根据筹码深度和底池赔率决策
    if (battleState.currentBet === player.currentBet) {
        // 没人下注，可以check或bet
        if (Math.random() < 0.7) {
            action = 'check';
        } else {
            action = 'bet';
        }
    } else if (callAmount <= player.chips) {
        // 需要跟注
        if (potOdds < 0.3 && Math.random() < 0.6) {
            action = 'call';
        } else if (player.chips > callAmount * 2 && Math.random() < 0.4) {
            action = 'raise';
        } else if (potOdds < 0.5 && Math.random() < 0.5) {
            action = 'call';
        } else {
            action = 'fold';
        }
    } else {
        // 筹码不够跟注，只能ALL IN或弃牌
        action = Math.random() < 0.3 ? 'allin' : 'fold';
    }
    
    console.log('[对战] AI', playerIndex, '(', player.position, ') 执行动作：', action, '筹码:', player.chips/100, 'bb');
    
    // 执行动作
    executeAction(playerIndex, action);
    
    // 移动到下一个玩家
    if (!battleState.gameOver) {
        moveToNextPlayer();
    }
}

function executeAction(playerIndex, action) {
    var player = battleState.players[playerIndex];
    if (!player || player.isFolded || player.isAllIn) return;
    
    switch(action) {
        case 'fold':
            player.isFolded = true;
            break;
        case 'check':
            if (battleState.currentBet > player.currentBet) return;
            break;
        case 'call':
            var callAmount = battleState.currentBet - player.currentBet;
            if (callAmount > 0) {
                var actualCall = Math.min(callAmount, player.chips);
                player.chips -= actualCall;
                player.currentBet += actualCall;
                player.totalBetThisHand += actualCall;
                battleState.pot += actualCall;
                if (player.chips === 0) player.isAllIn = true;
            }
            break;
        case 'bet':
        case 'raise':
            var betAmount = battleState.currentBet > 0 ? battleState.currentBet * 2 : 200;
            var actualBet = Math.min(betAmount, player.chips + player.currentBet);
            var additional = actualBet - player.currentBet;
            if (additional > 0) {
                player.chips -= additional;
                player.currentBet = actualBet;
                player.totalBetThisHand += additional;
                battleState.pot += additional;
                battleState.currentBet = actualBet;
                if (player.chips === 0) player.isAllIn = true;
            }
            break;
        case 'allin':
            var allinAmount = player.chips;
            player.chips = 0;
            player.currentBet += allinAmount;
            player.totalBetThisHand += allinAmount;
            battleState.pot += allinAmount;
            battleState.currentBet = Math.max(battleState.currentBet, player.currentBet);
            player.isAllIn = true;
            break;
    }
    
    checkBattleEnd();
    
    if (!battleState.gameOver) {
        moveToNextPlayer();
    }
}

function checkBattleEnd() {
    var player = battleState.players[battleState.playerSeatIndex];
    
    // 检查玩家是否输光
    if (player.chips <= 0 && !player.isAllIn) {
        battleState.gameOver = true;
        showBattleResult(false);
        return;
    }
    
    // 检查是否只剩一个未弃牌玩家
    var activePlayers = [];
    for (var a = 0; a < battleState.players.length; a++) {
        if (!battleState.players[a].isFolded) {
            activePlayers.push(battleState.players[a]);
        }
    }
    if (activePlayers.length === 1) {
        battleState.gameOver = true;
        var winner = activePlayers[0];
        showBattleResult(winner.isHuman);
        return;
    }
}

function showBattleResult(playerWon) {
    var player = battleState.players[battleState.playerSeatIndex];
    
    var message = '对战结束！\n\n';
    if (playerWon) {
        message += '🎉 你赢了这手牌！\n';
    } else {
        message += '😢 你输了这手牌\n';
    }
    message += '你的剩余筹码：' + (player.chips / 100).toFixed(1) + 'bb\n';
    message += '底池：' + (battleState.pot / 100).toFixed(1) + 'bb\n\n';
    message += '（完整对战循环正在开发中...）';
    
    alert(message);
    
    // 返回封面
    setTimeout(function() { goToCover(); }, 500);
}

// ==================== 修改现有函数 ====================
// 修改playerAction函数以支持对战模式
var originalPlayerAction = window.playerAction;
window.playerAction = function(action) {
    // 检查是否在对战模式
    if (typeof battleState !== 'undefined' && battleState.active) {
        handlePlayerAction(action);
    } else if (originalPlayerAction) {
        originalPlayerAction(action);
    }
};

// 修改startBattle函数
window.startBattle = function() {
    window.gameMode = 'battle';
    document.getElementById('coverScreen').classList.add('hidden');
    document.getElementById('gameScreen').classList.remove('hidden');
    
    // 隐藏难度选择器（对战模式不需要）
    var difficultySelector = document.querySelector('.difficulty-selector');
    if (difficultySelector) difficultySelector.style.display = 'none';
    
    // 隐藏练习模式的所有元素
    var practiceElements = document.querySelectorAll('.sidebar-card, .feedback-panel, .reasoning-section, .stats-row, .context-grid, .teaching-section, .mistakes-section, .opponent-range-section');
    for (var i = 0; i < practiceElements.length; i++) {
        practiceElements[i].style.display = 'none';
    }
    
    // 隐藏原来的对手信息（用座位代替）
    var opponentInfo = document.getElementById('opponentInfo');
    if (opponentInfo) opponentInfo.style.display = 'none';
    
    // 隐藏middle-panel（把动作按钮移到left-panel底部）
    var middlePanel = document.querySelector('.middle-panel');
    if (middlePanel) middlePanel.style.display = 'none';
    
    // 隐藏侧边栏（练习模式的）
    var sidebar = document.querySelector('.sidebar');
    if (sidebar) sidebar.style.display = 'none';
    
    // 把动作按钮移到left-panel底部
    var leftPanel = document.querySelector('.left-panel');
    var actionBar = document.querySelector('.action-bar');
    if (leftPanel && actionBar) {
        // 从原位置移除
        if (actionBar.parentNode) {
            actionBar.parentNode.removeChild(actionBar);
        }
        // 添加到left-panel底部
        leftPanel.appendChild(actionBar);
        // 显示action-bar
        actionBar.style.display = 'flex';
        // 调整样式
        actionBar.style.marginTop = 'auto';
        actionBar.style.padding = '1rem 0';
    }
    
    // 初始化对战
    initBattle();
    
    console.log('[对战] 对战模式启动完成，动作按钮已移至牌桌下方');
};

// 修改goToCover函数以恢复练习模式
var originalGoToCover = window.goToCover;
window.goToCover = function() {
    // 如果在对战模式，先清理
    if (typeof battleState !== 'undefined' && battleState.active) {
        battleState.active = false;
        window.gameMode = 'practice';
        
        // 恢复所有练习模式元素
        var practiceElements = document.querySelectorAll('.sidebar-card, .feedback-panel, .reasoning-section, .stats-row, .context-grid, .teaching-section, .mistakes-section, .opponent-range-section, .opponent-info');
        for (var i = 0; i < practiceElements.length; i++) {
            practiceElements[i].style.display = '';
        }
        
        // 恢复middle-panel
        var middlePanel = document.querySelector('.middle-panel');
        if (middlePanel) {
            var children = middlePanel.children;
            for (var j = 0; j < children.length; j++) {
                children[j].style.display = '';
            }
            middlePanel.style.display = '';
        }
        
        // 恢复sidebar
        var sidebar = document.querySelector('.sidebar');
        if (sidebar) sidebar.style.display = '';
        
        // 恢复difficulty-selector
        var difficultySelector = document.querySelector('.difficulty-selector');
        if (difficultySelector) difficultySelector.style.display = '';
        
        // 恢复left-panel
        var leftPanel = document.querySelector('.left-panel');
        if (leftPanel) leftPanel.style.display = '';
        
        // 把action-bar移回middle-panel
        var actionBar = document.querySelector('.action-bar');
        var originalMiddlePanel = document.querySelector('.middle-panel');
        if (actionBar && originalMiddlePanel && actionBar.parentNode !== originalMiddlePanel) {
            actionBar.parentNode.removeChild(actionBar);
            originalMiddlePanel.insertBefore(actionBar, originalMiddlePanel.firstChild);
            actionBar.style.marginTop = '';
            actionBar.style.padding = '';
        }
        
        // 移除对战座位
        var seats = document.querySelectorAll('.seat');
        for (var k = 0; k < seats.length; k++) {
            seats[k].parentNode.removeChild(seats[k]);
        }
    }
    
    // 调用原始goToCover
    if (originalGoToCover) {
        originalGoToCover();
    } else {
        window.gameState.gameStarted = false;
        document.getElementById('coverScreen').classList.remove('hidden');
        document.getElementById('gameScreen').classList.add('hidden');
    }
};

console.log('[对战] battle.js加载完成，startBattle已注册到全局');