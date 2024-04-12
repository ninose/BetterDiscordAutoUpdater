import os
from time import sleep
import json
import subprocess
import psutil
import requests
from typing import TypeVar, Tuple

from logging import getLogger, StreamHandler, DEBUG, INFO, basicConfig

from lib import countdown

T = TypeVar("T")


class BetterDiscorAutoUpdater:
    """
    Discord関連の自動インストーラークラス
    """

    def __init__(self, discord_client: str = "Discord") -> None:
        """
        BetterDiscorAutoUpdaterの初期化

        Parameters
        ----------
        discord_client : str, optional
            Discordのタイプ（"Discord", "DiscordPTB", "DiscordCanary"のいずれか）、デフォルトは"Discord"
        """
        self.logger = getLogger(__name__)
        basicConfig(format="(%(asctime)s) %(message)s")
        self.logger.setLevel(INFO)
        handler = StreamHandler()
        handler.setLevel(DEBUG)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(handler)
        self.logger.propagate = False

        self.discord_client: str = discord_client
        self.current_settings_version: int = 1
        self.settings_path: str = "settings.json"
        self.appdata: str = os.getenv("appdata") or ""
        self.localappdata: str = os.getenv("localappdata") or ""
        self.bd_asar_url: str = (
            "https://github.com/rauenzi/BetterDiscordApp/releases/latest/download/betterdiscord.asar"
        )
        self.bd_asar_save_path: str = os.path.join(
            self.appdata,
            f"BetterDiscord/data/betterdiscord_{self.discord_client.lower()}.asar",
        ).replace("\\", "/")
        self.discord_parent_path: str = ""
        self.discord_exe: str = f"{self.discord_client}.exe"

    def start_discord(self) -> None:
        """
        Discordを起動するメソッド
        """
        script_working_dir: str = os.path.dirname(os.path.abspath(__file__))
        os.chdir("c:/")
        subprocess.Popen(
            f'{os.path.join(self.discord_parent_path, "Update.exe")} --processStart {self.discord_exe}'
        )
        os.chdir(script_working_dir)

    def load_settings(self) -> None:
        """
        設定を読み込むメソッド
        """
        if os.path.exists(self.settings_path):
            with open(self.settings_path) as file:
                settings_data: dict = json.load(file)
                self.discord_parent_path: str = (
                    settings_data.get("discord_installed_path") or ""
                )
        else:
            self.discord_parent_path: str = f"{self.localappdata}/{self.discord_client}"

    def get_discord_path(self) -> None:
        """
        Discordのパスを取得するメソッド
        """
        while True:
            if not os.path.exists(os.path.join(self.discord_parent_path, "update.exe")):
                self.logger.info(
                    f'Discord {self.discord_client}のパス "{self.discord_parent_path}" には見つかりませんでした。 "Update.exe" があるフォルダのパスを入力してください：'
                )
                self.discord_parent_path = input("\n=> ")
                json.dump(
                    {"discord_installed_path": self.discord_parent_path},
                    open(self.settings_path, "w"),
                )
            else:
                break

    def check_discord_status(self) -> Tuple[bool, bool]:
        """
        Discordの状態をチェックするメソッド

        Returns
        -------
        Tuple[bool, bool]
            Discordが実行中かどうかと更新中かどうかのタプル
        """
        is_discord_running: bool = False
        is_discord_updating: bool = True

        for process in psutil.process_iter(["name"]):
            if process.info.get("name") == self.discord_exe:
                is_discord_running = True

                try:
                    for arg in process.cmdline():
                        if "--service-sandbox-type=audio" in arg:
                            is_discord_updating = False
                except psutil.NoSuchProcess:
                    pass

        return is_discord_running, is_discord_updating

    def install_discord(self) -> None:
        """
        Discordをインストールするメソッド
        """
        is_discord_running, self.is_discord_updating = self.check_discord_status()

        if not is_discord_running:
            discord_path = [
                i for i in os.listdir(self.discord_parent_path) if i.startswith("app-")
            ]
            discord_path.sort()
            discord_path = os.path.join(self.discord_parent_path, discord_path[-1])

            self.start_discord()
            self.logger.info(
                f"Discord {self.discord_client}のアップデーターが開始されました"
            )

            self.logger.info(
                f"Discord {self.discord_client}のアップデートの完了を待機中..."
            )
            quit_from_loop: bool = False

            while not quit_from_loop:
                for process in psutil.process_iter(["name"]):
                    if quit_from_loop:
                        break

                    if process.info["name"] == self.discord_exe:
                        try:
                            for arg in process.cmdline():
                                if "--service-sandbox-type=audio" in arg:
                                    countdown(5)
                                    quit_from_loop = True
                                    break
                        except psutil.NoSuchProcess:
                            pass

            self.logger.info(
                f"Discord {self.discord_client}のアップデートが完了しました。パッチを適用中..."
            )
            sleep(0.1)

            for process in psutil.process_iter(["name"]):
                if process.info["name"] == self.discord_exe and process.is_running():
                    process.kill()
            sleep(2)

    def patch_discord(self) -> None:
        """
        Discordの起動スクリプトをパッチするメソッド
        """
        discord_path = [
            i for i in os.listdir(self.discord_parent_path) if i.startswith("app-")
        ]
        discord_path.sort()
        discord_path = os.path.join(self.discord_parent_path, discord_path[-1])
        index_js_path: str = os.path.join(
            discord_path, "modules/discord_desktop_core-1/discord_desktop_core/index.js"
        )
        bd_required_folders: list[str] = [
            os.path.join(self.appdata, "BetterDiscord"),
            os.path.join(self.appdata, "BetterDiscord/data"),
            os.path.join(self.appdata, "BetterDiscord/themes"),
            os.path.join(self.appdata, "BetterDiscord/plugins"),
        ]

        self.logger.info("フォルダを作成中...")

        for folder in bd_required_folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

        self.logger.info("フォルダが作成されました！")

        self.logger.info("BetterDiscordの asar ファイルのダウンロードを試みています...")
        while True:
            try:
                response = requests.get(self.bd_asar_url)
            except requests.exceptions.ConnectionError:
                message = (
                    "asar ファイルのダウンロードに失敗しました。3秒後に再試行します..."
                )
                self.logger.info(message)
                countdown(3, message)
            else:
                with open(self.bd_asar_save_path, "wb") as file:
                    file.write(response.content)
                break

        self.logger.info("Asar ファイルのダウンロードが成功しました！")

        self.logger.info("Discordの起動スクリプトをパッチしています...")
        try:
            with open(index_js_path, "rb") as file:
                content = file.readlines()
        except FileNotFoundError as e:
            print("全てのアップデートが完了しました。")

        try:
            search_string = f"betterdiscord_{self.discord_client.lower()}.asar".encode()
            is_script_already_patched = [i for i in content if search_string in i]
        except UnboundLocalError as e:
            pass

        is_script_already_patched = bool(len(is_script_already_patched))

        if is_script_already_patched:
            self.logger.info("スクリプトはすでにパッチされています！")
        else:
            content.insert(0, f'require("{self.bd_asar_save_path}");\n'.encode())

            with open(index_js_path, "wb") as file:
                file.writelines(content)

            self.logger.info("パッチが完了しました！")

    def start_installer(self) -> None:
        """
        インストーラーを開始するメソッド
        """
        try:
            self.load_settings()
            self.get_discord_path()
            self.install_discord()
            self.patch_discord()

            for process in psutil.process_iter(["name"]):
                if process.info.get("name") == self.discord_exe:
                    process.kill()

            self.start_discord()
            self.logger.info(f"Discord {self.discord_client}が起動しました！")
            self.logger.info("インストールが完了しました！")
            countdown(3, "3秒後に終了します...")
        except:
            pass
        return 0

    # * これですべてのclientのupdateができる。
    def all_update(self) -> int:
        """
        all_update _summary_

        _extended_summary_

        Returns
        -------
        int
            正常終了の場合は0
        """
        self.install_discord(discord_client="Discord")
        self.install_discord(discord_client="DiscordPTB")
        self.install_discord(discord_client="DiscordCanary")
        return 0


def main() -> int:
    """
    メイン関数

    Returns
    -------
    int
        正常終了の場合は0
    """
    discord_installer = BetterDiscorAutoUpdater(discord_client="Discord")
    discord_installer.start_installer()

    discord_ptb_installer = BetterDiscorAutoUpdater(discord_client="DiscordPTB")
    discord_ptb_installer.start_installer()

    discord_canary_installer = BetterDiscorAutoUpdater(discord_client="DiscordCanary")
    discord_canary_installer.start_installer()
    return 0


if __name__ == "__main__":
    main()
