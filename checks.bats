#! /usr/bin/env bats

# Variable SUT_ID should be set outside this script and should contain the ID
# number of the System Under Test.

# Tests
@test 'configuration gridinit templatized' {
  run bash -c "sudo docker exec -ti ${SUT_ID} head -n 1 /etc/gridinit.conf"
  echo "output: "$output
  echo "status: "$status
  [[ "${status}" -eq "0" ]]
  [[ "${output}" =~ "Ansible managed" ]]
}


@test 'Namespace folder generation' {
	run bash -c "sudo docker exec -ti ${SUT_ID} bash -c 'find /etc/gridinit.d/ -type f|wc -l'"
  echo "output: "${output}
  echo "status: "$status
  [[ "${status}" -eq "0" ]]
  [[ "${output}" =~ "2" ]]
}

@test 'Status output' {
  run bash -c "sudo docker exec -ti ${SUT_ID} bash -c 'gridinit_cmd status|wc -l'"
  echo "output: "$output
  echo "status: "$status
  [[ "${status}" -eq "0" ]]
  [[ "${output}" =~ "3" ]]
}

@test 'File with a state "absent" is not present' {
  run bash -c "sudo docker exec -ti ${SUT_ID} bash -c 'find /etc/gridinit.d -type f|grep \"OPENIO2.rawx-1.conf\"'"
  echo "output: "$output
  echo "status: "$status
  [[ "${status}" -eq "1" ]]
}

