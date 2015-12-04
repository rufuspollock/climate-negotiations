---
title: Earth Negotiation Bulletins Archive
layout: default
wide: true
section: 
---

{% assign section_base = site.baseurl | append: 'enb' | append: '/' %}
<div class="stories">
  <div class="post-content">
  <h1 class="pre-header"><a href="/{{ section_base }}">{{ page.title }}</a></h1>
    <ul class="post-list">
      {% for story in site.pages | sort: 'date' %}
      {% if story.section == 'enb' %}
      <li>
        <h2>
          <a class="post-link" href="{{ story.url | prepend: site.baseurl }}">{{ story.title }}</a>
        </h2>
        {% if story.abstract %}
        <span class="post-excerpt">{{ story.abstract | markdownify | strip_html }}</span>
        {% else %}
        <span class="post-excerpt">{{ story.content | truncatewords: 50 | markdownify | strip_html }}</span>
        {% endif %}
        <a class="post-link" href="{{ story.url | prepend: site.baseurl }}">Read More</a>
      </li>
      {% endif %}
      {% endfor %}
    </ul>
  </div>
</div>
