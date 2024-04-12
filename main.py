from BetterDiscordAPI import BetterDiscorAutoUpdater

class Updater(BetterDiscorAutoUpdater):
    # Discordクライアントの種類
    DISCORD_CLIENT: str = "Discord"
    PTB_DISCORD_CLIENT: str = "DiscordPTB"
    DISCORD_CANARY_CLIENT: str = "DiscordCanary"
    CLIENT_LIST: list = [DISCORD_CLIENT, PTB_DISCORD_CLIENT, DISCORD_CANARY_CLIENT]

    def __init__(self, client: str = "Discord") -> None:
        """
        Updaterクラスの初期化関数です。

        Parameters
        ----------
        client : str, optional
            初期化時に設定するDiscordクライアントの名前です。デフォルトは "Discord" です。
        """
        self.discord_client = client
        super().__init__(discord_client=self.discord_client)

    def set_client(self, client: str = "Discord"):
        """
        Discordクライアントを設定します。

        Parameters
        ----------
        client : str, optional
            設定するDiscordクライアントの名前です。デフォルトは "Discord" です。

        Returns
        -------
        BetterDiscordAutoUpdater
            設定されたUpdaterインスタンスを返します。
        """
        self.discord_client = client
        super().__init__(discord_client=self.discord_client)
        return self

    def run(self):
        """
        インストーラーを実行します。

        Returns
        -------
        int
            正常に実行された場合は0を返します。
        """
        self.start_installer()
        return 0


def main() -> int:
    """
    メイン関数です。

    Returns
    -------
    int
        正常終了した場合は0を返します。
    """
    clients = Updater.CLIENT_LIST
    for client in clients:
        try:
            updater = Updater(client)
            updater.run()
        except Exception as e:
            print(f"{client}の更新中にエラーが発生しました: {e}")
    return 0


if __name__ == "__main__":
    main()
