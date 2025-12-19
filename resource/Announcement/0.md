使用手册 

## 如何使用？

1. 先打开新弹弹堂微信小程序 
2. 然后打开 DDTankAuto 程序，检查是否连接成功，可以在 **截图** - **截图测试** 进行测试看看能否捕获到正常画面。（如果连接失败，以管理员身份程序）。
3. 设置好参数，开始你想要的任务，可以上下拖动，或者点击加号来调整任务执行顺序。

## 注意事项

 
- 竞技场/多人副本扫荡多开方法：参考哔哩哔哩视频

## 常见问题

### Q: 无法下载最新资源、检查资源最新版发⽣错误？

A: 这是由于你网络问题，无法连接到GitHub导致的，建议使用加速器，或者加入Q群下载最新版。


### Q: 如何反馈问题，如何联系作者取得帮助。

在 [https://github.com/Tziheng/DDTankAuto/issues](https://github.com/Tziheng/DDTankAuto/issues) 提交 issue

加⼊Q群：469537326 反馈

详⻅公告反馈和建议

### Q: 打开软件没有我想要执行的任务。

A: 点击任务列表右上角的 + 号，添加目前已制作的任务。

### Q: 打开游戏时显示 “You must install or update .NET to run this application. ” 弹窗

A: 直接点击 “Download it now”即可，也可以在QQ群内下载 windowsdesktop-runtime-10.0.1-win-x64.exe 资源。

### Q: ⽆法打开界⾯。点击了DDTankAuto程序没有弹出窗⼝。 启动后闪退。

A: 在QQ群内下载 VC_redist.x64 2015-2022.exe 和 VC_redist.x64 2013.exe 解决。（安装后⽆需重启）

p.s. 如果找不到这两个⽂件可以前往微软官⽅⽹站下载

VC_redist.x64 2015-2022.exe: [https://learn.microsoft.com/zh-cn/cpp/windows/latest-supported-vcredist?view=msvc-170#latest-microsoft-visual-c-redistributable-version](https://learn.microsoft.com/zh-cn/cpp/windows/latest-supported-vcredist?view=msvc-170#latest-microsoft-visual-c-redistributable-version)

VC_redist.x64 2013.exe: [https://learn.microsoft.com/zh-cn/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2013-vc-120-no-longer-supported](https://learn.microsoft.com/zh-cn/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2013-vc-120-no-longer-supported)

### Q: 连接窗⼝时发⽣错误。截图测试时⿊屏。

A: ⼀般发⽣于启动 DDTankAuto 程序时没有“新弹弹堂”窗⼝或者“新弹弹堂”窗⼝处于最⼩化，可以关掉 DDTankAuto 程序，再重新打开。如果截图测试时依旧⿊屏，切换设置⾥“连接设置”的捕获⽅式，助手默认选择“PrintWindow”捕获方式。

### Q: 我重启了小程序，但是DDTankAuto程序就连接不上了。

A: 重启小程序操作等于关闭小程序再打开小程序。重新打开小程序导致“新弹弹堂”窗口句柄的改变，甚至包括窗口大小也会改变，你必须重新运行 DDTankAuto 程序。

### Q: 程序运⾏时⿏标点击位置不对。截图测试时游戏画⾯不全或者游戏画⾯过⼩。

A: 应该是窗⼝⼤⼩设置不正确导致的，重启 DDTankAuto 程序，看看日志里窗口大小是否设置成功。

### Q: 执⾏任务时，可以执⾏，但是不⾃动点击？

A: 切换设置⾥“连接设置”的触控模式，助手默认选择的是 “SendMessageWithCursorPos” 触控模式。

### Q: 定时启动任务时失败？

A: 如果勾选上了强制定时启动，可能会导致任务启动失败。强制定时启动会⽴刻停⽌当前任务并执⾏定时任务，由于当前任务未执⾏完成（没有返回到游戏主界⾯），可能会导致定时任务识别初始界⾯不是设定界⾯。
