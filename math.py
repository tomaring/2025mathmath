import tkinter as tk
from tkinter import messagebox
from itertools import permutations

class MagicSquareApp:
    def __init__(self, master):
        self.master = master
        master.title("魔法陣パズル")
        
        self.entries = {}  # 魔法陣(1-9)と外部マス(A-F)の入力フィールドを保持
        self.results = []  # 見つかった解を格納

        # 魔法陣と入力フィールドのレイアウトを作成
        self.create_widgets()
        
        # 結果表示用のフレームを作成
        self.result_frame = tk.Frame(master)
        self.result_frame.pack(pady=20)
        self.result_label = tk.Label(self.result_frame, text="結果はここに表示されます。", font=('Arial', 12))
        self.result_label.pack()

    ## 🎨 GUIコンポーネントの作成
    def create_widgets(self):
        main_frame = tk.Frame(self.master)
        main_frame.pack(padx=10, pady=10)

        # 1. 魔法陣の9マス（Grid 1-9）
        square_frame = tk.LabelFrame(main_frame, text="① 魔法陣の9マス (1〜9の数字を入力)")
        square_frame.grid(row=0, column=0, padx=10, pady=5)
        
        # 魔法陣の配置（3x3）
        for i in range(3):
            for j in range(3):
                # 内部番号: 1から9
                num = i * 3 + j + 1
                entry_key = f"M{num}" # M1, M2, ..., M9
                
                e = tk.Entry(square_frame, width=3, justify='center')
                e.grid(row=i, column=j, padx=2, pady=2)
                self.entries[entry_key] = e
                # 説明用のラベル（表示はしませんが、配置のイメージとして）
                # tk.Label(square_frame, text=str(num), font=('Arial', 7)).grid(row=i, column=j, sticky='nw')

        # 2. 右横の入力マス（A, B, C）
        right_frame = tk.LabelFrame(main_frame, text="A, B, C")
        right_frame.grid(row=0, column=1, padx=10, pady=5, sticky='n')
        
        for i, key in enumerate(['A', 'B', 'C']):
            label = tk.Label(right_frame, text=f"マス {key}:")
            label.grid(row=i, column=0, padx=5, pady=2, sticky='e')
            e = tk.Entry(right_frame, width=3, justify='center')
            e.grid(row=i, column=1, padx=5, pady=2)
            self.entries[key] = e
            
        # 3. 下の入力マス（D, E, F）
        bottom_frame = tk.LabelFrame(main_frame, text="D, E, F")
        bottom_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        
        for i, key in enumerate(['D', 'E', 'F']):
            label = tk.Label(bottom_frame, text=f"マス {key}:")
            label.grid(row=0, column=i*2, padx=5, pady=2, sticky='e')
            e = tk.Entry(bottom_frame, width=3, justify='center')
            e.grid(row=0, column=i*2 + 1, padx=5, pady=2)
            self.entries[key] = e

        # 4. 実行ボタン
        tk.Button(main_frame, text="残りの数字を入れる", command=self.solve, font=('Arial', 14, 'bold')).grid(row=2, column=0, columnspan=2, pady=20)
        

    ## 🔢 入力値の取得と前処理
    def get_input_values(self):
        # 魔法陣の入力値
        M = {} # 魔法陣マス(M1-M9)の値を格納 (int or None)
        # 外部入力値
        E = {} # 外部マス(A-F)の値を格納 (int or None)
        
        # 1-9, A-Fの全入力値を取得
        all_inputs = {}
        for key, entry in self.entries.items():
            value = entry.get().strip()
            if value:
                try:
                    all_inputs[key] = int(value)
                except ValueError:
                    messagebox.showerror("入力エラー", "すべての入力は数字（整数）でなければなりません。")
                    return None, None
            else:
                all_inputs[key] = None

        # 魔法陣のマスをMに、外部マスをEに振り分け
        for k, v in all_inputs.items():
            if k.startswith('M'):
                # M1〜M9の数字は1から9でなければならない制約をチェック（入力時）
                if v is not None and (v < 1 or v > 9):
                    messagebox.showerror("入力エラー", "魔法陣のマスには1〜9の数字のみ入力できます。")
                    return None, None
                M[int(k[1])] = v
            else:
                E[k] = v

        return M, E

    ## 🧩 探索と条件チェックのロジック
    def solve(self):
        M, E = self.get_input_values()
        if M is None or E is None:
            return

        # 1. すでに使用されている数字 (1-9) のリストと空のマス番号を特定
        used_numbers = set(v for v in M.values() if v is not None)
        empty_indices = [k for k, v in M.items() if v is None]
        
        # 2. 使用できる数字のセット (1-9のうち未使用のもの)
        available_numbers = [i for i in range(1, 10) if i not in used_numbers]
        
        # 3. 制約条件の確認（合計6個の数字を使用する）
        # 入力済みの数字の個数
        num_prefilled = len(used_numbers)
        # 埋めるべきマスの個数
        num_to_fill = len(empty_indices)
        
        # 全体で6個の数字を使うという制約
        if num_prefilled + num_to_fill != 6:
             messagebox.showerror("条件エラー", 
                                  f"魔法陣のマスに入力された数字は{num_prefilled}個、空きマスは{num_to_fill}個です。\n"
                                  f"合計6個のマスに1〜9の数字を割り当てる必要があります。\n"
                                  f"現在の合計は {num_prefilled + num_to_fill} 個です。"
                                 )
             return

        # 4. 探索に使用する数字のセット
        # available_numbersからnum_to_fill個の数字を選び、空のマスに割り当てる
        
        self.results = []
        self.clear_results()

        # available_numbersからnum_to_fill個の数字を選び、順列を生成
        # (6 - num_prefilled) 個の数字を、(9 - num_prefilled) 個の空きマスに割り当てる
        # ここで、空きマスの数が num_to_fill = 9 - num_prefilled
        # 割り当てる数字の個数が num_to_use = 6 - num_prefilled
        
        # 割り当てる数字の個数が num_to_fill よりも少ない場合はエラー
        num_to_use = 6 - num_prefilled
        if len(available_numbers) < num_to_use:
             messagebox.showerror("条件エラー", 
                                  f"1〜9の未使用の数字は{len(available_numbers)}個ですが、\n"
                                  f"残り{num_to_fill}マスを埋めるためにあと{num_to_use}個の数字が必要です。"
                                 )
             return
        
        
        # available_numbersから num_to_use 個の数字を選ぶ組み合わせを生成
        from itertools import combinations
        
        # 1. 割り当てる数字の組み合わせを選ぶ (available_numbersから num_to_use 個)
        for chosen_numbers_tuple in combinations(available_numbers, num_to_use):
            chosen_numbers = list(chosen_numbers_tuple)
            
            # 2. 選んだ数字を、空きマス (empty_indices) に割り当てる順列を生成
            # 割り当てる数字のリスト chosen_numbers の順列を作成
            for assignment_tuple in permutations(chosen_numbers, num_to_use):
                
                # 新しい魔法陣M_tempを作成し、入力済みの値と割り当てた値をセット
                M_temp = M.copy()
                assignment = list(assignment_tuple)
                
                # 空きマスに数字を割り当てる
                for i in range(num_to_use):
                    # empty_indices: 埋めるマスの番号 (1〜9)
                    # assignment: 割り当てる数字
                    M_temp[empty_indices[i]] = assignment[i]
                
                # 埋められなかったマス (9 - 6 = 3マス) は None のまま

                # 制約チェック
                if self.check_constraints(M_temp, E):
                    self.results.append(M_temp)
                    
        # 5. 結果の表示
        if self.results:
            self.display_results()
        else:
            self.result_label.config(text="「作れません」")


    ## ✅ 制約条件のチェック
    def check_constraints(self, M_final, E):
        
        # 最終的な魔法陣 M_final のうち、数字が入っているマスのみを考慮
        
        # 和が一致すべき値を保持する変数
        # total_sum は None で初期化し、最初の有効な和で設定する
        total_sum = None

        # --- 行の和 (A, B, C) ---
        row_sums = [
            E['A'] + M_final[1] + M_final[2] + M_final[3] if M_final[1] is not None else None, # 1, 2, 3
            E['B'] + M_final[4] + M_final[5] + M_final[6] if M_final[4] is not None else None, # 4, 5, 6
            E['C'] + M_final[7] + M_final[8] + M_final[9] if M_final[7] is not None else None  # 7, 8, 9
        ]
        
        for s in row_sums:
            if s is not None:
                if total_sum is None:
                    total_sum = s
                elif s != total_sum:
                    return False

        # --- 列の和 (D, E, F) ---
        col_sums = [
            E['D'] + M_final[1] + M_final[4] + M_final[7] if M_final[1] is not None else None, # 1, 4, 7
            E['E'] + M_final[2] + M_final[5] + M_final[8] if M_final[2] is not None else None, # 2, 5, 8
            E['F'] + M_final[3] + M_final[6] + M_final[9] if M_final[3] is not None else None  # 3, 6, 9
        ]
        
        for s in col_sums:
            if s is not None:
                if total_sum is None:
                    total_sum = s
                elif s != total_sum:
                    return False
                    
        # total_sum が None の場合（すべての和が計算できなかった場合）、条件は満たされない
        if total_sum is None:
            return False # 少なくとも一つの和が計算できる必要がある
            
        return True # すべての和が一致した（または一つも計算されず、total_sumが設定されなかったが、これは上記でFalseになる）

    ## 🖼 結果の表示
    def clear_results(self):
        # 既存の結果をクリア
        for widget in self.result_frame.winfo_children():
            widget.destroy()
            
    def display_results(self):
        self.clear_results()
        
        tk.Label(self.result_frame, text=f"✅ {len(self.results)}個の解が見つかりました！", font=('Arial', 14, 'bold'), fg='green').pack(pady=5)
        
        # 結果をスクロール可能なフレームに入れる
        canvas = tk.Canvas(self.result_frame, borderwidth=0, background="#ffffff")
        inner_frame = tk.Frame(canvas, background="#ffffff")
        vsb = tk.Scrollbar(self.result_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((4, 4), window=inner_frame, anchor="nw", 
                             tags="inner_frame")

        def onFrameConfigure(event):
            # スクロール領域の更新
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner_frame.bind("<Configure>", onFrameConfigure)

        
        # 見つかったすべての解を表示
        for i, M_final in enumerate(self.results):
            # 解の番号
            tk.Label(inner_frame, text=f"--- 解 {i+1} ---", font=('Arial', 12, 'underline')).pack(pady=5)
            
            result_grid = tk.Frame(inner_frame, borderwidth=1, relief="solid")
            result_grid.pack(padx=5, pady=5)
            
            # 3x3 の魔法陣を表示
            for r in range(3):
                for c in range(3):
                    # マス番号: M1からM9
                    num = r * 3 + c + 1
                    value = M_final[num]
                    
                    text = str(value) if value is not None else "－" # 空きマスは「－」
                    
                    # 埋めた数字を強調するために色を変える
                    bg_color = 'lightgray' if value is None else 'lightblue'

                    tk.Label(result_grid, 
                             text=text, 
                             width=4, 
                             height=2,
                             relief="solid", 
                             borderwidth=1,
                             font=('Arial', 12, 'bold'),
                             bg=bg_color).grid(row=r, column=c)


if __name__ == '__main__':
    root = tk.Tk()
    app = MagicSquareApp(root)
    root.mainloop()
