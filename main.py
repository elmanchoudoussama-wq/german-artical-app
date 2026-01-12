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

# --- 1. IMPORT LIBRARIES ---
try:
    from kivmob import KivMob
    HAS_KIVMOB = True
except ImportError:
    HAS_KIVMOB = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC_LIBS = True
except ImportError:
    HAS_ARABIC_LIBS = False

# --- ARABIC FIX FUNCTION ---
def fix_arabic(text):
    if not text or not HAS_ARABIC_LIBS:
        return text
    try:
        # Check if contains Arabic characters
        if any("\u0600" <= char <= "\u06FF" for char in text):
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)
    except:
        pass
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

# --- KV LAYOUT ---
# I added 'font_name' to every Arabic-facing label/button
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
            title: app.arabic_title
            font_name: "Amiri-Regular.ttf"

        MDScrollView:
            MDBoxLayout:
                id: stage_grid
                orientation: 'vertical'
                adaptive_height: True
                padding: "20dp"
                spacing: "15dp"

        BoxLayout:
            size_hint_y: None
            height: "50dp"

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
                        on_release: app.select_article(self.text)
                    MDFillRoundFlatButton:
                        id: article_btn2
                        text: app.article_options[1]
                        on_release: app.select_article(self.text)
                    MDFillRoundFlatButton:
                        id: article_btn3
                        text: app.article_options[2]
                        on_release: app.select_article(self.text)

                MDLabel:
                    text: app.arabic_meaning_label
                    font_name: "Amiri-Regular.ttf"
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
                    text: app.check_btn_text
                    font_name: "Amiri-Regular.ttf"
                    size_hint_x: 1
                    disabled: not app.submit_enabled
                    on_release: app.check_answer()

                MDLabel:
                    text: app.result_text
                    font_name: "Amiri-Regular.ttf"
                    halign: "center"
                    font_style: "H6"

<ResultScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: "30dp"
        spacing: "20dp"

        MDLabel:
            text: app.explanation_title
            font_name: "Amiri-Regular.ttf"
            halign: "center"
            font_style: "H4"
        
        MDLabel:
            text: app.explanation_text
            halign: "center"
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
    question_number = StringProperty("")
    article_options = ListProperty(["", "", ""])
    meaning_options = ListProperty(["", "", ""])
    submit_enabled = BooleanProperty(False)
    result_text = StringProperty("")
    explanation_text = StringProperty("")
    
    # Arabic Property Wrappers
    arabic_title = StringProperty("")
    arabic_meaning_label = StringProperty("")
    check_btn_text = StringProperty("")
    explanation_title = StringProperty("")

    # IDs (Keep Real for Build, Test for Debug)
    APP_ID = "ca-app-pub-9298331856947532~1106493604"
    BANNER_ID = "ca-app-pub-9298331856947532/4147412301"
    INTERSTITIAL_ID = "ca-app-pub-9298331856947532/7703513932"

    def build(self):
        LabelBase.register(name='Amiri-Regular.ttf', fn_regular='Amiri-Regular.ttf')
        self.arabic_title = fix_arabic("تعلم الأرتيكل")
        self.arabic_meaning_label = fix_arabic("المعنى:")
        self.check_btn_text = fix_arabic("تحقق")
        self.explanation_title = fix_arabic("شرح")
        
        self.theme_cls.primary_palette = "Blue"
        self.ad_settings = AdSettings()

        if platform == 'android' and HAS_KIVMOB:
            try:
                self.ads = KivMob(self.APP_ID)
                self.ads.new_banner(self.BANNER_ID, top_pos=False)
                self.ads.request_banner()
                self.ads.new_interstitial(self.INTERSTITIAL_ID)
                self.ads.request_interstitial()
            except: self.ads = None
        else: self.ads = None
        
        return Builder.load_string(KV_STRING)

    def on_start(self):
        self.load_progress()
        self.build_stage_menu()
        if self.ads: self.ads.show_banner()

    def load_progress(self):
        self.unlocked_stages = 1
        if os.path.exists('progress.json'):
            try:
                with open('progress.json', 'r') as f:
                    self.unlocked_stages = json.load(f).get('unlocked', 1)
            except: pass

    def build_stage_menu(self):
        grid = self.root.get_screen('stage_select').ids.stage_grid
        grid.clear_widgets()
        layout = MDGridLayout(cols=3, adaptive_height=True, spacing="10dp")
        for i in range(1, 101):
            locked = i > self.unlocked_stages
            btn = MDFillRoundFlatButton(
                text=f"{i}", disabled=locked,
                on_release=lambda x, s=i: self.load_stage(s)
            )
            layout.add_widget(btn)
        grid.add_widget(layout)

    def load_stage(self, s):
        self.current_stage = s
        path = f'data/stages/stage_{s}.json'
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.nouns = json.load(f)
            self.unused = list(self.nouns)
            self.question_count = 1
            self.correct_count = 0
            self.generate_question()
            self.root.current = 'main'

    def generate_question(self):
        self.submit_enabled = False
        self.result_text = ""
        item = random.choice(self.unused)
        
        # Reshape meanings immediately
        correct_meaning = fix_arabic(item['meaning'])
        other_meanings = [fix_arabic(n['meaning']) for n in self.nouns if n['meaning'] != item['meaning']]
        m_choices = [correct_meaning] + random.sample(other_meanings, min(len(other_meanings), 2))
        random.shuffle(m_choices)
        
        self.current_q = item
        self.sentence = item['sentences'].get('Nominativ', item['word'])
        self.question_number = f"Stage {self.current_stage} - {self.question_count}/11"
        self.article_options = random.sample(['der', 'die', 'das', 'den', 'dem'], 3)
        if item['article'] not in self.article_options: self.article_options[0] = item['article']
        random.shuffle(self.article_options)
        self.meaning_options = m_choices

    def select_article(self, t): self.sel_art = t
    def select_meaning(self, t): 
        self.sel_mean = t
        self.submit_enabled = True

    def check_answer(self):
        if self.sel_art == self.current_q['article'] and self.sel_mean == fix_arabic(self.current_q['meaning']):
            self.result_text = fix_arabic("إجابة صحيحة ✅")
            Clock.schedule_once(lambda dt: self.next_question(), 1)
        else:
            self.explanation_text = fix_arabic(f"خطأ! الصحيح هو: {self.current_q['article']} {self.current_q['word']}")
            self.root.current = 'result'

    def next_question(self):
        if self.question_count >= 11:
            if self.ads: self.ads.show_interstitial()
            self.root.current = 'stage_select'
        else:
            self.question_count += 1
            self.generate_question()

    def handle_stage_quit(self):
        self.root.current = 'stage_select'

if __name__ == '__main__':
    GermanArticleTrainer().run()
