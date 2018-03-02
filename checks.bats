#! /usr/bin/env bats

# Variable SUT_ID should be set outside this script and should contain the ID
# number of the System Under Test.

# Tests
@test 'configuration gridinit templatized' {
  run bash -c "docker exec -ti ${SUT_ID} head -n 1 /etc/gridinit.conf"
  echo "output: "$output
  echo "status: "$status
  [[ "${status}" -eq "0" ]]
  [[ "${output}" =~ "Ansible managed" ]]
}


@test 'Namespace folder generation' {
	run bash -c "docker exec -ti ${SUT_ID} ls /etc/gridinit.d | tr -s \"\t\" ' '"
  echo "output: "$output
  echo "status: "$status
  [[ "${status}" -eq "0" ]]
  [[ "${output}" =~ "OPENIO OPENIO2" ]]
}

@test 'File with a state "absent" is not present' {
  run bash -c "docker exec -ti ${SUT_ID} ls /etc/gridinit.d/OPENIO2/rawx-1.conf"
  echo "output: "$output
  echo "status: "$status
  [[ "${status}" -eq "2" ]]
}

@test 'Status output' {
  run bash -c "docker exec -ti ${SUT_ID} bash -c 'gridinit_cmd status' | tail -n1 | tr -s ' ' ' '"
  echo "output: "$output
  echo "status: "$status
  [[ "${status}" -eq "0" ]]
  [[ "${output}" =~ "OPENIO-meta1-1 BROKEN -1 OPENIO,meta1,meta1-1" ]]
}
