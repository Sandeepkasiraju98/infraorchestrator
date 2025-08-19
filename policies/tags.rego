package terraform.tags

deny[msg] {
  required := {"owner", "env"}
  provided := {k | v := input.resource.values.tags; k := v[_]}
  not required ⊆ provided
  msg := "Missing required tags: owner, env"
}