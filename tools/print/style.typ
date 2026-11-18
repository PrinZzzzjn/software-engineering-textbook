// 教材样书版式。改版式只动这一段参数。
#let meta = (
  title: "软件工程实践（2.0）",
  subtitle: "送审样书",
  date: "2026 年 11 月",
)

#let fonts = (
  body: ("Times New Roman", "SimSun"),
  head: ("SimHei",),
  mono: ("Consolas", "Segoe UI Symbol"),
  kai: ("KaiTi", "STKaiti"),
)

#let body-size = 10.5pt
#let line-gap = 0.72em
#let para-gap = 1.05em
#let indent = 2em
#let margins = (top: 25mm, bottom: 25mm, inside: 30mm, outside: 22mm)
#let part-size = 28pt
#let chapter-size = 22pt
#let h2-size = 15pt
#let h3-size = 12pt
#let h4-size = 10.5pt
#let pseudo-size = 11pt
#let caption-size = 9pt
#let code-size = 8.5pt

#let chapter-state = state("chapter", "")

// 整本模板：正文前加 `#show: template` 即套用全部版式
#let template(body) = {
  set page(
    paper: "a4",
    margin: margins,
    binding: left,
    numbering: n => numbering("i", n - 1),
    header: context {
      let p = counter(page).get().first()
      let name = chapter-state.get()
      if name == "" { name = meta.title }
      set text(size: 8.5pt, font: fonts.head, fill: rgb("#333333"))
      if calc.odd(p) {
        align(right, name)
      } else {
        align(left, meta.title)
      }
      v(-2pt)
      line(length: 100%, stroke: 0.5pt + rgb("#777777"))
    },
    footer: context {
      align(center, text(size: 9pt, font: fonts.body, counter(page).display()))
    },
  )

  set text(font: fonts.body, size: body-size, lang: "zh", region: "cn", fill: rgb("#000000"))
  set par(
    leading: line-gap,
    spacing: para-gap,
    justify: true,
    first-line-indent: (amount: indent, all: true),
  )
  // 代码里的直引号必须保持直引号
  set smartquote(enabled: false)

  // 篇扉页
  show heading.where(level: 1): it => block(
    width: 100%,
    above: 0em,
    below: 2em,
    align(center, text(font: fonts.head, size: part-size, weight: "regular", it.body)),
  )

  // 章 / 卷首篇目
  show heading.where(level: 2): it => block(
    width: 100%,
    above: 2.2em,
    below: 1.6em,
    align(center, text(font: fonts.head, size: chapter-size, weight: "regular", it.body)),
  )

  // 二级标题（Markdown 的 ##）：居中
  show heading.where(level: 3): it => block(
    width: 100%,
    above: 2.2em,
    below: 1em,
    align(center, text(font: fonts.head, size: h2-size, weight: "regular", it.body)),
  )

  show heading.where(level: 4): it => block(
    above: 1.6em,
    below: 0.7em,
    text(font: fonts.head, size: h3-size, weight: "regular", it.body),
  )

  show heading.where(level: 5): it => block(
    above: 1.3em,
    below: 0.6em,
    text(font: fonts.head, size: h4-size, weight: "bold", it.body),
  )

  // 代码块：浅灰底 + 左侧灰竖线（是否可跨页由 code-group 决定）
  show raw.where(block: true): it => block(
    width: 100%,
    fill: rgb("#F6F6F6"),
    inset: (x: 8pt, y: 6pt),
    stroke: (left: 1.5pt + rgb("#BBBBBB")),
    above: 0.3em,
    below: 0.3em,
    text(size: code-size, font: fonts.mono, it),
  )

  // 行内代码
  show raw.where(block: false): it => box(
    fill: rgb("#F2F2F2"),
    inset: (x: 1.6pt, y: 0.6pt),
    outset: (y: 0pt),
    text(size: 9.5pt, font: fonts.mono, it),
  )

  // 表格：三线表，表内 9pt，首行不缩进，表头加粗
  show table: it => {
    set text(size: 9pt)
    set par(first-line-indent: 0em)
    it
  }

  show table.cell.where(y: 0): set text(weight: "bold", font: fonts.head)

  // 列表项不缩进首行
  show list: it => {
    set par(first-line-indent: 0em)
    it
  }

  body
}

// 篇扉页：单独一页，无页眉页脚页码
#let part(no, title) = page(
  header: none,
  footer: none,
  numbering: none,
  {
    v(1fr)
    heading(level: 1, outlined: true, bookmarked: true)[#no #title]
    v(1fr)
  },
)

// 卷首篇目与附录：另起页，计入目录，更新页眉
#let section(label) = {
  chapter-state.update(label)
  pagebreak(weak: true)
  heading(level: 2, outlined: true, bookmarked: true, label)
}

#let chapter(no, title) = section([#no #title])

// 目录页
#let toc-page() = {
  chapter-state.update("目录")
  pagebreak(weak: true)
  heading(level: 2, outlined: false, bookmarked: true)[目录]
  show outline.entry: set block(above: 0.45em)
  show outline.entry.where(level: 1): set text(weight: "bold")
  outline(title: none, depth: 2, indent: auto)
}

// mermaid 图：居中，最大宽 150mm
#let fig-image(src, width: 92%, height: none) = block(
  width: 100%,
  above: 0.9em,
  below: 0.2em,
  breakable: false,
  align(center, if height == none { image(src, width: width) } else { image(src, height: height) }),
)

// 图 + 题注作为整体，避免题注与图分页
#let fig-group(body) = block(
  width: 100%,
  above: 0.9em,
  below: 1em,
  breakable: false,
  body,
)

// 勾选式条目：去掉项目符号，只留 □ / ■
#let task-list(body) = {
  set list(marker: none)
  set par(first-line-indent: 0em)
  body
}

// 正文里的独立加粗段，充当节内小标题；number 为空时不编号
#let pseudo-heading(body, number: none) = block(
  width: 100%,
  above: 1.8em,
  below: 0.7em,
  {
    set par(first-line-indent: 0em)
    if number == none {
      text(font: fonts.head, size: pseudo-size, weight: "bold", body)
    } else {
      text(font: fonts.head, size: pseudo-size, weight: "bold")[#number #body]
    }
  },
)

// 提示 / 注意类引用块
#let callout(body) = block(
  width: 100%,
  inset: (left: 9pt, right: 4pt, y: 4pt),
  stroke: (left: 2pt + rgb("#999999")),
  above: 0.7em,
  below: 0.7em,
  {
    set par(first-line-indent: 0em)
    set text(font: fonts.kai)
    body
  },
)

// 代码组：说明行 + 代码块作为整体；短块不跨页，长块允许跨页
#let code-group(body, long: false) = block(
  width: 100%,
  above: 0.9em,
  below: 0.8em,
  breakable: long,
  body,
)

// 代码说明行：**代码 5-1-5** · 命令（Bash）
#let code-caption(body) = block(
  width: 100%,
  above: 0em,
  below: 0.15em,
  breakable: false,
  {
    set par(first-line-indent: 0em)
    text(size: caption-size, font: fonts.body, body)
  },
)

// 图题注：图下居中，不跨页
#let fig-caption(body) = block(
  width: 100%,
  above: 0.35em,
  below: 1.1em,
  breakable: false,
  align(center, text(size: caption-size, font: fonts.body, body)),
)
