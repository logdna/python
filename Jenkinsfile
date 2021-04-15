library 'magic-butler-catalogue'
def PROJECT_NAME = 'logdna-python'
def TRIGGER_PATTERN = ".*@logdnabot.*"
def DEFAULT_BRANCH = 'master'
def CURRENT_BRANCH = [env.CHANGE_BRANCH, env.BRANCH_NAME]?.find{branch -> branch != null}

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

      stages {
        stage('dry run') {
          when {
            not {
              branch "${DEFAULT_BRANCH}"
            }
          }

          environment {
            GH_TOKEN = credentials('github-api-token')
            PYPI_TOKEN = credentials('pypi-token')
            JENKINS_URL = "${JENKINS_URL}"
            BRANCH_NAME = "${DEFAULT_BRANCH}"
            GIT_BRANCH = "${DEFAULT_BRANCH}"
            CHANGE_ID = ''
          }

          steps {
            sh "make release-dry"
          }
        }

        stage('publish') {

          environment {
            GH_TOKEN = credentials('github-api-token')
            PYPI_TOKEN = credentials('pypi-token')
            JENKINS_URL = "${JENKINS_URL}"
          }

          when {
            branch "${DEFAULT_BRANCH}"
            not {
              changelog '\\[skip ci\\]'
            }
          }
          steps {
            sh 'make release'
          }
        }
      }
    }
  }
}
