---
layout: page
title: About
description: 多走一步，多看一步
keywords: 生活，学习，感悟
comments: true
menu: 关于
permalink: /about/
---
This is my own site to record the experience for my study and work.

## 联系

<ul>

<li>
</li>

</ul>


## Skill Keywords

{% for skill in site.data.skills %}
### {{ skill.name }}
<div class="btn-inline">
{% for keyword in skill.keywords %}
<button class="btn btn-outline" type="button">{{ keyword }}</button>
{% endfor %}
</div>
{% endfor %}
