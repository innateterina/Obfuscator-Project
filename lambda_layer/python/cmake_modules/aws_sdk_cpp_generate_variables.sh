#!/bin/bash
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

set -eu

version=$1

base_dir="$(dirname "$0")"
output="${base_dir}/AWSSDKVariables.cmake"

cat <<HEADER > ${output}
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# Generated by:
#   $ cpp/cmake_modules/aws_sdk_cpp_generate_variables.sh ${version}

HEADER

rm -f ${version}.tar.gz
wget https://github.com/aws/aws-sdk-cpp/archive/${version}.tar.gz
base_name=aws-sdk-cpp-${version}
rm -rf ${base_name}
tar xf ${version}.tar.gz

echo "set(AWSSDK_UNUSED_DIRECTORIES" >> ${output}
find ${base_name} -mindepth 1 -maxdepth 1 -type d | \
  sort | \
  grep -v cmake | \
  grep -v toolchains | \
  grep -v aws-cpp-sdk-cognito-identity | \
  grep -v aws-cpp-sdk-core | \
  grep -v aws-cpp-sdk-config | \
  grep -v aws-cpp-sdk-s3 | \
  grep -v aws-cpp-sdk-transfer | \
  grep -v aws-cpp-sdk-identity-management | \
  grep -v aws-cpp-sdk-sts | \
  sed -E -e "s,^${base_name}/,    ,g" >> ${output}
echo ")" >> ${output}

rm -rf ${base_name}
rm -f ${version}.tar.gz
