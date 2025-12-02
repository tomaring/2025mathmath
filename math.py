from itertools import permutations, combinations

# ----------------------------------------------------
# 1. データ構造と入力処理
# ----------------------------------------------------

def get_user_input():
    """
    ユーザーから魔法陣 (M1-M9) と外部マス (A-F) の入力を受け取る。
    空欄は None として扱う。
    """
    
    # 魔法陣のマス (M1〜M9)
    M = {}
    print("--- 魔法陣の9マス (M1〜M9) の入力 ---")
    print("  ※ 1〜9の数字を入力。空欄の場合はEnterキーを押してください。")
    print("  ※ 割り当てる数字の合計は6個になるように調整してください。")
    for i in range(1, 10):
        while True:
            try:
                # ユーザー入力を取得
                value_str = input(f"M{i} の値: ").strip()
                if not value_str:
                    M[i] = None
                    break
                
                value = int(value_str)
                # M1〜M9は1〜9の数字でなければならない
                if 1 <= value <= 9:
                    M[i] = value
                    break
                else:
                    print("エラー: 1〜9の数字を入力してください。")
            except ValueError:
                print("エラー: 無効な入力です。数字または空欄で入力してください。")

    # 外部のマス (A-F)
    E = {}
    print("\n--- 外部の6マス (A〜F) の入力 ---")
    print("  ※ A, B, C は右横、D, E, F は下の入力マスです。")
    for key in ['A', 'B', 'C', 'D', 'E', 'F']:
        while True:
            try:
                value_str = input(f"{key} の値: ").strip()
                if not value_str:
                    E[key] = None
                    break
                
                value = int(value_str)
                E[key] = value
                break
            except ValueError:
                print("エラー: 無効な入力です。数字または空欄で入力してください。")
                
    return M, E

# ----------------------------------------------------
# 2. 制約チェックと探索ロジック
# ----------------------------------------------------

def check_constraints(M_final, E, total_sum):
    """
    指定された魔法陣の配置 M_final が、すべての和の条件を満たすかチェックする。
    """
    
    # 外部マスが未入力の場合、和は比較できないため、NoneであればTrueとする
    
    # --- 行の和 (A, B, C) ---
    # A + M1 + M2 + M3 の和が total_sum と一致するか [cite: 11]
    if E['A'] is not None:
        current_sum = E['A'] + M_final[1] + M_final[2] + M_final[3]
        if current_sum != total_sum: return False

    # B + M4 + M5 + M6 の和が total_sum と一致するか [cite: 11]
    if E['B'] is not None:
        current_sum = E['B'] + M_final[4] + M_final[5] + M_final[6]
        if current_sum != total_sum: return False
        
    # C + M7 + M8 + M9 の和が total_sum と一致するか [cite: 11]
    if E['C'] is not None:
        current_sum = E['C'] + M_final[7] + M_final[8] + M_final[9]
        if current_sum != total_sum: return False

    # --- 列の和 (D, E, F) ---
    # D + M1 + M4 + M7 の和が total_sum と一致するか [cite: 11]
    if E['D'] is not None:
        current_sum = E['D'] + M_final[1] + M_final[4] + M_final[7]
        if current_sum != total_sum: return False
        
    # E + M2 + M5 + M8 の和が total_sum と一致するか [cite: 11]
    if E['E'] is not None:
        current_sum = E['E'] + M_final[2] + M_final[5] + M_final[8]
        if current_sum != total_sum: return False
        
    # F + M3 + M6 + M9 の和が total_sum と一致するか [cite: 11]
    if E['F'] is not None:
        current_sum = E['F'] + M_final[3] + M_final[6] + M_final[9]
        if current_sum != total_sum: return False

    return True

def solve_magic_square(M, E):
    """
    与えられた入力から、条件を満たす魔法陣のすべての解を探索する。
    """
    # 1. 初期設定と制約チェック
    used_numbers = set(v for v in M.values() if v is not None)
    empty_indices = [k for k, v in M.items() if v is None]
    
    num_prefilled = len(used_numbers)
    num_to_fill = len(empty_indices)
    
    # 魔法陣に割り当てる数字の合計は6個 
    num_to_use = 6 - num_prefilled 

    if num_prefilled + num_to_fill < 6:
        print("エラー: 既に数字が入っているマスと空きマスの合計が6個未満です。合計6個になるように入力してください。")
        return []
    
    if num_to_fill < num_to_use:
         print("エラー: 空きマスの数 ({num_to_fill}個) が、埋めるべき数字の数 ({num_to_use}個) より少ないです。")
         return []

    # 2. 探索に使用できる数字のセット (1〜9のうち未使用のもの)
    available_numbers = [i for i in range(1, 10) if i not in used_numbers]
    
    if len(available_numbers) < num_to_use:
        print(f"エラー: 1〜9の未使用の数字は{len(available_numbers)}個ですが、あと{num_to_use}個の数字が必要です。")
        return []
        
    solutions = []

    # 3. 共通の和 (total_sum) の決定
    
    # 既に和が計算できる行/列があれば、その値を共通の和とする
    fixed_sum = None
    
    # 和が計算できるすべての組み合わせ
    # (外部マスがNoneでない AND 魔法陣の対応する3マスすべてに数字が入っている)
    
    sums_to_check = []
    
    # 行
    row_indices = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
    external_keys = ['A', 'B', 'C']
    for indices, key in zip(row_indices, external_keys):
        if E[key] is not None and all(M[i] is not None for i in indices):
            sums_to_check.append(E[key] + sum(M[i] for i in indices))
    
    # 列
    col_indices = [(1, 4, 7), (2, 5, 8), (3, 6, 9)]
    external_keys = ['D', 'E', 'F']
    for indices, key in zip(col_indices, external_keys):
        if E[key] is not None and all(M[i] is not None for i in indices):
            sums_to_check.append(E[key] + sum(M[i] for i in indices))
            
    if sums_to_check:
        # すべての和が一致していなければ、初期入力で既に矛盾している
        if len(set(sums_to_check)) > 1:
            print("エラー: 入力された数字で既に、和が一致しない組み合わせが存在します。")
            return []
        fixed_sum = sums_to_check[0]

    # 4. バックトラッキングと探索
    
    # available_numbersから num_to_use 個の数字を選ぶ組み合わせを生成
    for chosen_numbers_tuple in combinations(available_numbers, num_to_use):
        
        # 選んだ数字を、空きマス (empty_indices) に割り当てる順列を生成
        for assignment_tuple in permutations(chosen_numbers_tuple, num_to_use):
            
            M_temp = M.copy()
            
            # 空きマスに数字を割り当てる
            for i in range(num_to_use):
                M_temp[empty_indices[i]] = assignment_tuple[i]
            
            # 埋められなかったマス (9 - 6 = 3マス) は None のまま

            # total_sumの計算（最初の有効な和を取得）
            current_total_sum = fixed_sum
            
            if current_total_sum is None:
                # 暫定的な配置で和が計算できる行/列があるか確認
                for indices, key in zip(row_indices, external_keys[:3]):
                    if E[key] is not None:
                        current_total_sum = E[key] + sum(M_temp[i] for i in indices)
                        break
                if current_total_sum is None:
                    for indices, key in zip(col_indices, external_keys[3:]):
                        if E[key] is not None:
                            current_total_sum = E[key] + sum(M_temp[i] for i in indices)
                            break
            
            # 制約チェックの実行
            # current_total_sum が None の場合、和が計算できる行/列が存在しないため、制約を満たせない
            if current_total_sum is not None and check_constraints(M_temp, E, current_total_sum):
                solutions.append(M_temp)
                    
    return solutions

# ----------------------------------------------------
# 3. 出力処理
# ----------------------------------------------------

def display_results(solutions):
    """
    見つかったすべての解を整形して出力する。
    """
    print("\n" + "="*40)
    if not solutions:
        print("「作れません」")
    else:
        print(f"✅ {len(solutions)}個の解が見つかりました！")
        print("="*40)
        
        for i, M_final in enumerate(solutions):
            print(f"\n--- 解 {i+1} ---")
            
            # 3x3 の魔法陣を表示
            # 魔法陣の番号の配置 [cite: 5]
            # 1 2 3
            # 4 5 6
            # 7 8 9
            
            grid_output = []
            for r in range(3):
                row = []
                for c in range(3):
                    # マス番号: 1から9
                    num = r * 3 + c + 1
                    value = M_final[num]
                    # None の場合は「-」を表示
                    row.append(f"{str(value):^3}" if value is not None else " - ")
                grid_output.append(" ".join(row))
            
            print("\n".join(grid_output))
            
            # 外部マスと和のチェック
            
            # 共通の和を再計算（解が出た時点では必ず一つ以上の和が計算可能）
            total_sum = None
            
            # 行の和
            row_indices = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
            external_keys = ['A', 'B', 'C']
            for indices, key in zip(row_indices, external_keys):
                if E[key] is not None:
                    total_sum = E[key] + sum(M_final[i] for i in indices)
                    break
            
            # 列の和
            if total_sum is None:
                col_indices = [(1, 4, 7), (2, 5, 8), (3, 6, 9)]
                external_keys = ['D', 'E', 'F']
                for indices, key in zip(col_indices, external_keys):
                    if E[key] is not None:
                        total_sum = E[key] + sum(M_final[i] for i in indices)
                        break

            print(f"\n共通の和: {total_sum}")

# ----------------------------------------------------
# 4. メイン実行ブロック
# ----------------------------------------------------

def main():
    while True:
        print("\n\n" + "*"*50)
        print("   魔法陣パズルソルバー (CUI版)   ")
        print("*"*50)
        
        # ① 入力
        M, E = get_user_input()
        
        # ② 探索と出力
        solutions = solve_magic_square(M, E)
        display_results(solutions)
        
        # 繰り返しの確認
        print("\n" + "-"*50)
        again = input("もう一度試しますか？ (y/n): ").strip().lower()
        if again != 'y':
            print("アプリケーションを終了します。")
            break

if __name__ == "__main__":
    main()
