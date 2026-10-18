import random
import time

# ============================================================
# 1. КОНСТАНТЫ И СЛОВАРИ
# ============================================================

SYMBOLS = {
    "🍒": {"weight": 30, "payout": 5,   "name": "Вишня"},
    "🍋": {"weight": 25, "payout": 8,   "name": "Лимон"},
    "🔔": {"weight": 18, "payout": 15,  "name": "Колокол"},
    "💎": {"weight": 10, "payout": 50,  "name": "Алмаз"},
    "7️⃣": {"weight": 4,  "payout": 100, "name": "Семёрка"},
    "👑": {"weight": 1,  "payout": "JACKPOT", "name": "Корона"},
}

PAYTABLE = {
    "triple": {
        "🍒": 5,
        "🍋": 8,
        "🔔": 15,
        "💎": 50,          # BIG DROP
        "7️⃣": 100,         # MEGA DROP
        "👑": "JACKPOT",   # весь джекпот-банк
    },
    "double": 2,
    "none": 0,
}

GAME_CONFIG = {
    "starting_balance": 1000,
    "starting_bet": 10,
    "jackpot_contribution_rate": 0.01,
    "starting_jackpot": 500,
    "min_bet": 1,
    "reels_count": 3,
}

STATS = {
    "spins": 0,
    "wins": 0,
    "losses": 0,
    "big_drops": 0,
    "jackpots": 0,
    "biggest_win": 0,
    "total_wagered": 0,
    "total_won": 0,
}

COMMANDS = {
    "spin": "spin", "s": "spin", "крутить": "spin",
    "bet": "bet", "b": "bet", "ставка": "bet",
    "balance": "balance", "bal": "balance", "баланс": "balance",
    "stats": "stats", "st": "stats", "стата": "stats",
    "paytable": "paytable", "pt": "paytable", "выплаты": "paytable",
    "help": "help", "h": "help", "?": "help", "помощь": "help",
    "quit": "quit", "q": "quit", "exit": "quit", "выход": "quit",
    "reset": "reset", "r": "reset", "сброс": "reset",
}

MESSAGES = {
    "win_small":  ["💸 Неплохо!", "✨ Мелочь, а приятно!", "🎯 Есть контакт!"],
    "win_medium": ["🔥 Хороший занос!", "💰 Казна пополняется!", "🎊 Уже теплее!"],
    "big_drop":   ["💥💥💥 BIG DROP! 💥💥💥", "🚀 ЭТО БОЛЬШОЙ ДРОП!", "💎 ДИАМАНТОВЫЙ ЗАНОС!"],
    "mega_drop":  ["🔥🔥🔥 MEGA DROP! 🔥🔥🔥", "☄️ СЕМЁРКИ РВУТ БАЛАНС!", "🏆 ЭПИЧЕСКИЙ ЗАНОС!"],
    "jackpot":    ["👑👑👑 JACKPOT!!! 👑👑👑", "🎉 ДЖЕКПОТ СОРВАН!", "🌟 КОРОНА ТВОЯ!"],
    "loss":       ["😬 Не повезло, крути ещё!", "🙈 Почти!", "🎲 Барабаны капризны..."],
    "no_money":   "❌ Недостаточно средств. Уменьши ставку (`bet <число>`).",
    "bad_bet":    "❌ Неверная ставка. Нужно целое число от min_bet до баланса.",
    "game_over":  "💀 Баланс 0. Игра окончена. Введи `reset` для новой игры.",
    "unknown":    "❓ Неизвестная команда. Введи `help` для списка команд.",
}

REEL_FRAMES = ["🍒", "🍋", "🔔", "💎", "7️⃣", "👑", "🍒", "🍋"]


# ============================================================
# 2. СОСТОЯНИЕ ИГРЫ
# ============================================================

class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.balance = GAME_CONFIG["starting_balance"]
        self.bet = GAME_CONFIG["starting_bet"]
        self.jackpot = GAME_CONFIG["starting_jackpot"]
        for key in STATS:
            STATS[key] = 0


# ============================================================
# 3. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def print_banner():
    print("=" * 55)
    print("🎰  CONSOLE CASINO — BIG DROP EDITION  🎰".center(55))
    print("=" * 55)
    print("  Введи `help` для списка команд.\n")


def show_help():
    print("\n📖 КОМАНДЫ:")
    print("  spin   (s, крутить)    — крутить барабаны")
    print("  bet N  (b, ставка)     — поставить N кредитов")
    print("  balance(bal, баланс)   — показать баланс и джекпот")
    print("  stats  (st, стата)     — статистика игры")
    print("  paytable(pt, выплаты)  — таблица выплат")
    print("  reset  (r, сброс)      — сбросить игру")
    print("  quit   (q, выход)      — выйти\n")


def show_balance(state):
    print(f"\n💰 Баланс: {state.balance}  |  🎯 Ставка: {state.bet}  |  👑 Джекпот-банк: {state.jackpot:.0f}\n")


def show_paytable():
    print("\n📊 ТАБЛИЦА ВЫПЛАТ (три одинаковых символа):")
    print(f"  {'Символ':<6} {'Имя':<12} {'Вес':<6} {'Множитель'}")
    print("  " + "-" * 40)
    for sym, info in SYMBOLS.items():
        payout = info["payout"]
        payout_str = "ДЖЕКПОТ" if payout == "JACKPOT" else f"×{payout}"
        print(f"  {sym:<6} {info['name']:<12} {info['weight']:<6} {payout_str}")
    print("\n  Два одинаковых символа → ×2")
    print("  Три разных символа     → проигрыш\n")


def show_stats():
    print("\n📈 СТАТИСТИКА:")
    print(f"  Спинов:            {STATS['spins']}")
    print(f"  Выигрышей:         {STATS['wins']}")
    print(f"  Проигрышей:        {STATS['losses']}")
    print(f"  BIG DROPS:         {STATS['big_drops']}")
    print(f"  ДЖЕКПОТОВ:         {STATS['jackpots']}")
    print(f"  Макс. выигрыш:     {STATS['biggest_win']}")
    print(f"  Всего поставлено:  {STATS['total_wagered']}")
    print(f"  Всего выиграно:    {STATS['total_won']}")
    profit = STATS["total_won"] - STATS["total_wagered"]
    sign = "+" if profit >= 0 else ""
    print(f"  Чистый профит:     {sign}{profit}\n")


def parse_bet(arg, state):
    try:
        value = int(arg)
    except (ValueError, TypeError):
        return None
    if value < GAME_CONFIG["min_bet"] or value > state.balance:
        return None
    return value


# ============================================================
# 4. ЛОГИКА БАРАБАНОВ И ВЫИГРЫША
# ============================================================

def spin_reels():
    population = list(SYMBOLS.keys())
    weights = [SYMBOLS[s]["weight"] for s in population]
    return random.choices(population, weights=weights, k=GAME_CONFIG["reels_count"])


def evaluate_spin(reels):
    a, b, c = reels
    if a == b == c:
        return "triple", PAYTABLE["triple"][a], a
    if a == b or b == c or a == c:
        return "double", PAYTABLE["double"], None
    return "none", PAYTABLE["none"], None


def animate_reels(final_reels):
    for _ in range(6):
        fake = [random.choice(REEL_FRAMES) for _ in range(GAME_CONFIG["reels_count"])]
        print("\r  🎰  " + "  ".join(fake), end="", flush=True)
        time.sleep(0.1)
    print("\r  🎰  " + "  ".join(final_reels) + "   ")


# ============================================================
# 5. ОСНОВНАЯ ИГРОВАЯ ЛОГИКА
# ============================================================

def do_spin(state):
    if state.balance <= 0:
        print(MESSAGES["game_over"])
        return
    if state.bet > state.balance:
        print(MESSAGES["no_money"])
        return

    # списываем ставку
    state.balance -= state.bet
    STATS["spins"] += 1
    STATS["total_wagered"] += state.bet

    # 1% в джекпот-банк
    state.jackpot += state.bet * GAME_CONFIG["jackpot_contribution_rate"]

    # крутим
    reels = spin_reels()
    print()
    animate_reels(reels)

    kind, payout, symbol = evaluate_spin(reels)

    win = 0
    message_pool = None

    if kind == "triple":
        if payout == "JACKPOT":
            win = int(state.jackpot)
            state.jackpot = GAME_CONFIG["starting_jackpot"]
            STATS["jackpots"] += 1
            message_pool = MESSAGES["jackpot"]
        else:
            win = state.bet * payout
            if payout >= 100:
                STATS["big_drops"] += 1
                message_pool = MESSAGES["mega_drop"]
            elif payout >= 50:
                STATS["big_drops"] += 1
                message_pool = MESSAGES["big_drop"]
            else:
                message_pool = MESSAGES["win_medium"] if payout >= 8 else MESSAGES["win_small"]
    elif kind == "double":
        win = state.bet * payout
        message_pool = MESSAGES["win_small"]
    else:
        message_pool = MESSAGES["loss"]

    # обновляем баланс и статистику
    state.balance += win
    if win > 0:
        STATS["wins"] += 1
        STATS["total_won"] += win
        if win > STATS["biggest_win"]:
            STATS["biggest_win"] = win
        print(random.choice(message_pool))
        print(f"  💵 Выигрыш: +{win} кредитов!")
    else:
        STATS["losses"] += 1
        print(random.choice(message_pool))

    show_balance(state)


def do_bet(arg, state):
    if not arg:
        print("❌ Укажи ставку: `bet <число>`")
        return
    new_bet = parse_bet(arg, state)
    if new_bet is None:
        print(MESSAGES["bad_bet"])
        return
    state.bet = new_bet
    print(f"✅ Ставка установлена: {state.bet}")


def do_reset(state):
    confirm = input("Сбросить игру? (yes/no): ").strip().lower()
    if confirm in ("yes", "y", "да"):
        state.reset()
        print("🔄 Игра сброшена. Удачи!")
        show_balance(state)
    else:
        print("Отмена.")


# ============================================================
# 6. ГЛАВНЫЙ ЦИКЛ
# ============================================================

def main():
    state = GameState()
    print_banner()
    show_balance(state)

    while True:
        try:
            raw = input("🎲 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Пока!")
            break

        if not raw:
            continue

        parts = raw.split()
        cmd_key = parts[0].lower()
        cmd = COMMANDS.get(cmd_key)

        if cmd is None:
            print(MESSAGES["unknown"])
            continue

        if cmd == "spin":
            do_spin(state)
        elif cmd == "bet":
            arg = parts[1] if len(parts) > 1 else None
            do_bet(arg, state)
        elif cmd == "balance":
            show_balance(state)
        elif cmd == "stats":
            show_stats()
        elif cmd == "paytable":
            show_paytable()
        elif cmd == "help":
            show_help()
        elif cmd == "reset":
            do_reset(state)
        elif cmd == "quit":
            print("👋 Спасибо за игру! Возвращайся за BIG DROP.")
            break


if __name__ == "__main__":
    main()