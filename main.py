from kivy.utils import platform
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from kivymd.uix.button import MDFillRoundFlatButton, MDFlatButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.core.text import LabelBase
import json
import random
import os
import time

# --- 1. IMPORT KIVMOB ---
try:
    from kivmob import KivMob, TestIds
    HAS_KIVMOB = True
except ImportError:
    HAS_KIVMOB = False

# --- ARABIC SUPPORT ---
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC_LIBS = True
except ImportError:
    HAS_ARABIC_LIBS = False

def fix_arabic(text):
    if not text: return ""
    if HAS_ARABIC_LIBS:
        try:
            return get_display(arabic_reshaper.reshape(text))
        except: return text
    return text

# --- AD SETTINGS ---
class AdSettings:
    def __init__(self):
        self.AD_FILE = 'ad_data.json'
        self.default_ad_data = {'last_24h_ad': 0, 'question_count': 0}
        self.load_ad_data()
    
    def load_ad_data(self):
        if os.path.exists(self.AD_FILE):
            try:
                with open(self.AD_FILE, 'r') as f:
                    self.data = json.load(f)
            except: self.data = self.default_ad_data.copy()
        else: self.data = self.default_ad_data.copy()
    
    def save_ad_data(self):
        with open(self.AD_FILE, 'w') as f: json.dump(self.data, f)
    
    def check_24h_ad_required(self):
        return (time.time() - self.data.get('last_24h_ad', 0)) >= 3600 # 3 hours for testing
    
    def update_24h_ad_watched(self):
        self.data['last_24h_ad'] = time.time()
        self.save_ad_data()
    
    def increment_question_count(self):
        self.data['question_count'] = self.data.get('question_count', 0) + 1
        self.save_ad_data()
    
    def check_stage_quit_ad(self):
        return self.data.get('question_count', 0) >= 5
    
    def reset_question_count(self):
        self.data['question_count'] = 0
        self.save_ad_data()

# --- MOCK AD DIALOGS (For PC Testing) ---
class MockAdDialog(ModalView):
    def __init__(self, title, message, on_complete, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.4)
        self.auto_dismiss = False
        self.on_complete = on_complete
        
        card = MDBoxLayout(orientation='vertical', padding="20dp", spacing="10dp")
        card.md_bg_color = (1, 1, 1, 1)
        
        card.add_widget(MDLabel(text=title, halign='center', font_style='H6'))
        card.add_widget(MDLabel(text=message, halign='center'))
        
        btn = MDFillRoundFlatButton(text="SIMULATE WATCH AD (PC ONLY)", pos_hint={'center_x': 0.5})
        btn.bind(on_release=self.finish)
        card.add_widget(btn)
        self.add_widget(card)

    def finish(self, *args):
        self.dismiss()
        if self.on_complete: self.on_complete()

# --- KV LAYOUT (Kept your structure) ---
KV_STRING = '''
ScreenManager:
    StageSelectScreen:
        name: 'stage_select'
    MainScreen:
        name: 'main'
    ResultScreen:
        name: 'result'

<StageSelectScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.95, 0.95, 0.95, 1
        
        MDTopAppBar:
            title: app.get_arabic_title()
            font_name: "Amiri-Regular.ttf"

        MDScrollView:
            MDBoxLayout:
                id: stage_grid
                orientation: 'vertical'
                adaptive_height: True
                padding: "20dp"
                spacing: "15dp"

        # Spacer for Banner Ad
        BoxLayout:
            size_hint_y: None
            height: "50dp"
            MDLabel:
                text: "Ad Space"
                halign: "center"
                theme_text_color: "Hint"

<MainScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1

        MDTopAppBar:
            title: app.question_number
            left_action_items: [["arrow-left", lambda x: app.handle_stage_quit()]]
            elevation: 2

        MDScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                adaptive_height: True
                padding: "20dp"
                spacing: "20dp"
                
                MDLabel:
                    text: app.sentence
                    halign: "center"
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None

                MDGridLayout:
                    cols: 3
                    spacing: "10dp"
                    size_hint_y: None
                    height: "60dp"
                    
                    MDFillRoundFlatButton:
                        id: article_btn1
                        text: app.article_options[0]
                        size_hint_x: 1
                        on_release: app.select_article(self.text)
                    
                    MDFillRoundFlatButton:
                        id: article_btn2
                        text: app.article_options[1]
                        size_hint_x: 1
                        on_release: app.select_article(self.text)

                    MDFillRoundFlatButton:
                        id: article_btn3
                        text: app.article_options[2]
                        size_hint_x: 1
                        on_release: app.select_article(self.text)

                MDLabel:
                    text: "Bedeutung:"
                    halign: "center"
                    font_style: "Subtitle1"
                    size_hint_y: None
                    height: "30dp"

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: "10dp"
                    adaptive_height: True
                    
                    MDFillRoundFlatButton:
                        id: meaning_btn1
                        text: app.meaning_options[0]
                        font_name: "Amiri-Regular.ttf"
                        size_hint_x: 1
                        on_release: app.select_meaning(self.text)
                    
                    MDFillRoundFlatButton:
                        id: meaning_btn2
                        text: app.meaning_options[1]
                        font_name: "Amiri-Regular.ttf"
                        size_hint_x: 1
                        on_release: app.select_meaning(self.text)
                    
                    MDFillRoundFlatButton:
                        id: meaning_btn3
                        text: app.meaning_options[2]
                        font_name: "Amiri-Regular.ttf"
                        size_hint_x: 1
                        on_release: app.select_meaning(self.text)

                MDFillRoundFlatButton:
                    text: "PRÜFEN"
                    size_hint_x: 1
                    disabled: not app.submit_enabled
                    md_bg_color: (0, 0.7, 0, 1) if self.disabled == False else (0.8, 0.8, 0.8, 1)
                    on_release: app.check_answer()

                MDLabel:
                    text: app.result_text
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0, 0.6, 0, 1
                    font_style: "H6"
                    size_hint_y: None
                    height: self.texture_size[1]
        
        # Spacer for Banner Ad
        BoxLayout:
            size_hint_y: None
            height: "50dp"

<ResultScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: "30dp"
        spacing: "20dp"
        md_bg_color: 1, 0.95, 0.95, 1

        MDLabel:
            text: "Erklärung"
            halign: "center"
            font_style: "H4"
        
        MDLabel:
            text: app.explanation_text
            halign: "center"
            font_style: "Body1"
            font_name: "Amiri-Regular.ttf"

        MDFillRoundFlatButton:
            text: "Weiter"
            pos_hint: {"center_x": 0.5}
            on_release: app.next_question()
'''

class StageSelectScreen(Screen): pass
class MainScreen(Screen): pass
class ResultScreen(Screen): pass

class GermanArticleTrainer(MDApp):
    sentence = StringProperty("")
    question_number = StringProperty("Frage #1")
    article_options = ListProperty(["", "", ""])
    meaning_options = ListProperty(["", "", ""])
    submit_enabled = BooleanProperty(False)
    result_text = StringProperty("")
    explanation_text = StringProperty("")
    current_stage = NumericProperty(1)
    unlocked_stages = NumericProperty(1)
    QUESTIONS_PER_STAGE = 11

    # --- AD CONFIGURATION ---
    # REPLACE THESE WITH YOUR REAL IDs FROM ADMOB CONSOLE
    APP_ID = "ca-app-pub-9298331856947532~1106493604" # Test ID
    
    BANNER_ID = "ca-app-pub-9298331856947532/4147412301" # Test ID
    
    INTERSTITIAL_ID = "ca-app-pub-9298331856947532/7703513932" # Test ID


    def get_arabic_title(self):
        return fix_arabic("Artical lernen")

    def build(self):
        # Font Registration
        font_path = 'Amiri-Regular.ttf'
        if os.path.exists(font_path):
            LabelBase.register(name='Amiri-Regular.ttf', fn_regular=font_path)
        
        self.theme_cls.primary_palette = "Blue"
        self.ad_settings = AdSettings()

        # --- INITIALIZE KIVMOB ---
        self.ads = None
        if platform == 'android' and HAS_KIVMOB:
            # Initialize KivMob
            self.ads = KivMob(self.APP_ID)
            
            # Setup Banner
            self.ads.new_banner(self.BANNER_ID, top_pos=False) # False = Bottom
            self.ads.request_banner()
            
            # Setup Interstitial (Full Screen)
            self.ads.new_interstitial(self.INTERSTITIAL_ID)
            self.ads.request_interstitial()
        
        return Builder.load_string(KV_STRING)

    def on_start(self):
        self.load_progress()
        self.ensure_data_exists()
        self.build_stage_menu()
        
        # Show Banner immediately
        if self.ads:
            self.ads.show_banner()
            
        # Check 24h Ad
        Clock.schedule_once(self.check_24h_ad, 1)

    # --- AD LOGIC WRAPPERS ---
    def show_interstitial_ad(self, on_close_callback=None):
        """Logic to show ad on Android or Mock dialog on PC"""
        self._ad_callback = on_close_callback
        
        if self.ads:
            # Real Android Ad
            if self.ads.is_interstitial_loaded():
                self.ads.show_interstitial()
                # Request next ad immediately for future use
                self.ads.request_interstitial()
                if on_close_callback:
                    on_close_callback()
            else:
                # Ad wasn't ready, request one and proceed
                self.ads.request_interstitial()
                if on_close_callback:
                    on_close_callback()
        else:
            # PC / Mock Ad
            MockAdDialog(
                title="Interstitial Ad", 
                message="This is where a full screen Google ad appears.",
                on_complete=on_close_callback
            ).open()

    # --- DATA & GAME LOGIC ---
    def load_progress(self):
        if os.path.exists('progress.json'):
            try:
                with open('progress.json', 'r') as f:
                    self.unlocked_stages = json.load(f).get('unlocked', 1)
            except: self.unlocked_stages = 1

    def save_progress(self):
        with open('progress.json', 'w') as f:
            json.dump({'unlocked': self.unlocked_stages}, f)

    def build_stage_menu(self):
        screen = self.root.get_screen('stage_select')
        grid = screen.ids.stage_grid
        grid.clear_widgets()
        self.button_grid = MDGridLayout(adaptive_height=True, spacing="10dp")
        grid.add_widget(self.button_grid)

        for i in range(1, 101):
            is_locked = i > self.unlocked_stages
            btn = MDFillRoundFlatButton(
                text=f"Stage {i}" if not is_locked else f"S{i} Locked",
                size_hint=(1, None),
                disabled=is_locked,
                md_bg_color=self.theme_cls.primary_color if not is_locked else (0.7, 0.7, 0.7, 1),
                on_release=lambda x, s=i: self.load_stage(s)
            )
            self.button_grid.add_widget(btn)
        
        self.update_grid_cols()
        Window.bind(on_resize=self.update_grid_cols)

    def update_grid_cols(self, *args):
        new_cols = max(2, int(Window.width / dp(110)))
        if hasattr(self, 'button_grid'): self.button_grid.cols = new_cols

    def load_stage(self, stage_number):
        self.current_stage = stage_number
        try:
            with open(f'data/stages/stage_{stage_number}.json', 'r', encoding='utf-8') as f:
                self.nouns = json.load(f)
            self.unused_nouns = list(self.nouns)
            random.shuffle(self.unused_nouns)
            self.question_count = 1
            self.correct_count = 0
            
            self.ad_settings.increment_question_count()
            self.generate_question()
            self.root.current = 'main'
            
        except FileNotFoundError:
            print(f"Error: Missing Stage {stage_number}")

    def check_answer(self):
        article_correct = (self.selected_article_choice == self.current_question['article_in_case'])
        meaning_correct = (self.selected_meaning_choice == self.current_question['meaning'])
        self.apply_result_colors()

        if article_correct and meaning_correct:
            self.result_text = "✅ Richtig!"
            self.correct_count += 1
            Clock.schedule_once(lambda dt: self.next_question(), 1.0)
        else:
            self.result_text = "❌ Falsch"
            self.explanation_text = f"Wort: {self.current_question['noun']}\nBedeutung: {self.current_question['meaning']}\nFall: {self.current_question['case']}\nRichtig: {self.current_question['article_in_case']}"
            Clock.schedule_once(lambda dt: setattr(self.root, 'current', 'result'), 1.0)

    def next_question(self):
        if self.question_count >= self.QUESTIONS_PER_STAGE:
            self.finish_stage()
            return
        self.question_count += 1
        self.ad_settings.increment_question_count()
        self.generate_question()
        self.root.current = 'main'

    def finish_stage(self):
        score_percent = (self.correct_count / self.QUESTIONS_PER_STAGE) * 100
        success = score_percent >= 90
        msg = f"Du hast {self.correct_count}/{self.QUESTIONS_PER_STAGE} richtig ({score_percent:.0f}%)."
        if success:
            title = "Stufe Bestanden! 🎉"
            if self.current_stage == self.unlocked_stages:
                self.unlocked_stages += 1
                self.save_progress()
                self.build_stage_menu()
        else:
            title = "Nicht genug Punkte"
            msg += "\nDu brauchst 90%."

        dialog = MDDialog(
            title=title, text=msg,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.close_dialog_and_exit(dialog))]
        )
        dialog.open()
        
        # SHOW AD AFTER STAGE
        self.show_interstitial_ad()

    def close_dialog_and_exit(self, dialog):
        dialog.dismiss()
        self.go_back_to_menu()

    def handle_stage_quit(self):
        if self.ad_settings.check_stage_quit_ad():
            # Show Ad then quit
            self.show_interstitial_ad(on_close_callback=self.go_back_to_menu)
        else:
            self.go_back_to_menu()

    def go_back_to_menu(self):
        self.root.transition.direction = 'right'
        self.root.current = 'stage_select'
        self.ad_settings.reset_question_count()

    def generate_question(self):
        self.selected_article_choice = ""
        self.selected_meaning_choice = ""
        self.submit_enabled = False
        self.result_text = ""

        if not self.unused_nouns:
            self.unused_nouns = list(self.nouns)
            random.shuffle(self.unused_nouns)
        noun_data = self.unused_nouns.pop()

        cases = {'Nominativ': {'der': 'der', 'die': 'die', 'das': 'das'},
                 'Akkusativ': {'der': 'den', 'die': 'die', 'das': 'das'},
                 'Dativ': {'der': 'dem', 'die': 'der', 'das': 'dem'}}
        case = random.choice(['Nominativ', 'Akkusativ', 'Dativ'])
        correct_article = cases[case][noun_data['article']]
        correct_meaning = fix_arabic(noun_data['meaning'])

        all_articles = ['der', 'die', 'das', 'den', 'dem']
        wrong_articles = [a for a in all_articles if a != correct_article]
        article_choices = [correct_article] + random.sample(wrong_articles, 2)
        random.shuffle(article_choices)

        other_meanings = list(set([fix_arabic(n['meaning']) for n in self.nouns if fix_arabic(n['meaning']) != correct_meaning]))
        if len(other_meanings) >= 2: meaning_choices = [correct_meaning] + random.sample(other_meanings, 2)
        else: meaning_choices = [correct_meaning, "Wort 1", "Wort 2"]
        random.shuffle(meaning_choices)

        self.current_question = {'noun': noun_data['word'], 'meaning': correct_meaning,
                                 'sentence': noun_data['sentences'].get(case, ""), 'case': case,
                                 'article_in_case': correct_article}
        self.sentence = self.current_question['sentence']
        self.question_number = f"Stufe {self.current_stage} - {self.question_count}/{self.QUESTIONS_PER_STAGE}"
        self.article_options = article_choices
        self.meaning_options = meaning_choices
        self.reset_button_colors()

    def reset_button_colors(self):
        screen = self.root.get_screen('main')
        for i in range(1, 4):
            for p in ['article_btn', 'meaning_btn']:
                btn = screen.ids.get(f'{p}{i}')
                if btn:
                    btn.md_bg_color = self.theme_cls.primary_color

    def select_article(self, t):
        self.selected_article_choice = t
        self.update_colors('article_btn', t)
        self.submit_enabled = bool(self.selected_article_choice and self.selected_meaning_choice)

    def select_meaning(self, t):
        self.selected_meaning_choice = t
        self.update_colors('meaning_btn', t)
        self.submit_enabled = bool(self.selected_article_choice and self.selected_meaning_choice)

    def update_colors(self, prefix, txt):
        screen = self.root.get_screen('main')
        for i in range(1, 4):
            btn = screen.ids.get(f'{prefix}{i}')
            if btn: btn.md_bg_color = (0.1, 0.1, 0.4, 1) if btn.text == txt else self.theme_cls.primary_color

    def apply_result_colors(self):
        screen = self.root.get_screen('main')
        for i in range(1, 4):
            btn_a = screen.ids.get(f'article_btn{i}')
            if btn_a and btn_a.text == self.current_question['article_in_case']: btn_a.md_bg_color = (0, 0.5, 0, 1)
            elif btn_a and btn_a.text == self.selected_article_choice: btn_a.md_bg_color = (0.8, 0, 0, 1)
            
            btn_m = screen.ids.get(f'meaning_btn{i}')
            if btn_m and btn_m.text == self.current_question['meaning']: btn_m.md_bg_color = (0, 0.5, 0, 1)
            elif btn_m and btn_m.text == self.selected_meaning_choice: btn_m.md_bg_color = (0.8, 0, 0, 1)

    # --- AD CHECKS ---
    def check_24h_ad(self, dt=None):
        if self.ad_settings.check_24h_ad_required():
            def on_complete():
                self.ad_settings.update_24h_ad_watched()
            self.show_interstitial_ad(on_complete)
    
    def ensure_data_exists(self):
        os.makedirs('data/stages', exist_ok=True)
        if not os.path.exists('data/stages/stage_1.json'):
             # Create dummy data if needed
             pass

if __name__ == '__main__':
    GermanArticleTrainer().run()
