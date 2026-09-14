"""Scope approved CSS above Elementor defaults without editing vendor packages."""

from __future__ import annotations

import tinycss2


def scope_stylesheet(css: str) -> str:
    def walk(rules, keyframes=False):
        output = []
        for rule in rules:
            if rule.type == "at-rule" and rule.content is not None:
                if rule.lower_at_keyword in ["media", "supports", "layer", "container"]:
                    nested = tinycss2.parse_rule_list(rule.content, skip_whitespace=False, skip_comments=False)
                    rule.content = tinycss2.parse_component_value_list(walk(nested))
            elif rule.type == "qualified-rule" and not keyframes:
                groups = []
                current = []
                for token in rule.prelude:
                    if token.type == "literal" and token.value == ",":
                        groups.append(tinycss2.serialize(current).strip())
                        current = []
                    else:
                        current.append(token)
                groups.append(tinycss2.serialize(current).strip())
                scoped = []
                for selector in groups:
                    if selector.startswith(("html", ":root")):
                        scoped.append(selector)
                    elif selector.startswith("body"):
                        scoped.append("body.hc-native.hc-native.hc-native" + selector[4:])
                    elif selector.startswith(".home-page"):
                        scoped.append(".hc-native.hc-native.hc-native" + selector)
                    else:
                        scoped.append(".hc-native.hc-native.hc-native " + selector)
                rule.prelude = tinycss2.parse_component_value_list(",".join(scoped))
            output.append(tinycss2.serialize([rule]))
        return "".join(output)

    return walk(tinycss2.parse_stylesheet(css, skip_whitespace=False, skip_comments=False))
