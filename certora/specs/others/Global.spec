definition globalInvariant(env e) returns bool =
  e.msg.sender != 0;

rule globalVacuityRule(method f) {
	env e; calldataarg args;
	f(e, args);
	assert false, "Testing Vacuity, failure means OK!";
}
