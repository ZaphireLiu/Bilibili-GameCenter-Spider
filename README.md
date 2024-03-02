# Bilibili-GameCenter-Spider
B站游戏中心评价区爬虫

简单练习一下Python爬虫，因为B站游戏中心评价区的api中引入了`request_id`和`appkey`两个校验值，不好用request的方法直接获取评价区内容，所以用了`selenium`来获取具体内容。

使用Edge浏览器，需要提前下载[Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH)，通过简单的修改应该也适用于其他浏览器。

## 使用的库

```
seleniumwire
selenium
bs4
```

## 功能介绍

按时间最近-最早的顺序爬取b站游戏评论区，目前爬取的内容有：
1. 用户id
2. 评价时间
3. 评分
4. 评价内容
5. 评价获得的赞和踩

实际还可以获得评价的评论和评论的赞，不过我没用到就没写。

爬取的内容以数页为一个单位，存放在json文件中。

单条评论的例子如下：
```
    {
        "userid": "179945326",
        "time": "2024-03-02 18:31:57",
        "text": "\u597d\u60f3\u73a9\u554a 2/11\n\u77e2 3/1",
        "up_count": 3,
        "down_count": 2,
        "star_num": 1
    }
```
评论文本以Unicode的形式保存。

## 存在问题

尚不清楚是我的代码问题还是库的问题，在其中几次运行中，seleniumwire用于抓取HTML源代码的代理线程会报错，但实际上不影响使用。
