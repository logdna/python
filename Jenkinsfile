library 'magic-butler-catalogue'
def PROJECT_NAME = 'logdna-python'
def TRIGGER_PATTERN = ".*@logdnabot.*"
def DEFAULT_BRANCH = 'master'

pipeline {
  agent none

  options {
    timestamps()
    ansiColor 'xterm'
  }

  triggers {
    issueCommentTrigger(TRIGGER_PATTERN)
  }

  stages {
    stage('Test') {
      agent {
        node {
          label 'ec2-fleet'
          customWorkspace "${PROJECT_NAME}-${BUILD_NUMBER}"
        }
      }

      steps {
        sh 'make install lint test'
      }

      post {
        always {
          junit 'coverage/test.xml'
          publishHTML target: [
            allowMissing: false,
            alwaysLinkToLastBuild: false,
            keepAll: true,
            reportDir: 'coverage',
            reportFiles: 'index.html',
            reportName: "coverage-${BUILD_TAG}"
          ]
        }
      }
    }

    stage('Release') {
      agent {
        node {
          label 'ec2-fleet'
          customWorkspace "${PROJECT_NAME}-${BUILD_NUMBER}"
        }
      }

      environment {
        GH_TOKEN = credentials('github-api-token')
        PYPI_TOKEN = credentials('pypi-token')
      }

      steps {
        script {
          if ("${BRANCH_NAME}" == "${DEFAULT_BRANCH}") {
            sh 'make release'
          } else {
            sh "BRANCH_NAME=${DEFAULT_BRANCH} CHANGE_ID='' make release-dry"
          }
        }
      }
    }
  }
}
