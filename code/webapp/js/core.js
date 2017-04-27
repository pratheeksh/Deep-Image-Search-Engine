var searchApp = angular.module('searchApp', ['ngSanitize']).config(
    function($locationProvider) {
        $locationProvider.html5Mode(true);
    });

searchApp.controller('mainController', function ($scope, $http, $location) {
    $scope.formData = {};

    $scope.search = function() {
        if ($scope.formData.query) {
            $location.search('q', $scope.formData.query);
        }
    };

    $scope.fetchRecords = function() {
        var start = new Date().getTime();
        $http.get('/search?q=' + encodeURIComponent($scope.formData.query)).success(function(data) {
            $scope.delay = (new Date().getTime() - start) / 1000.0;
            $scope.totalItems = data.num_results;
            $scope.errorText = data.error;
            $scope.results = data.results;
        }).error(function(data) {
            $scope.results = [];
            $scope.totalItems = 0;
            $scope.errorText = data;
        });
    };

    $scope.$on('$locationChangeSuccess', function(event){
        if ($location.search().q) {
            $scope.formData.query = $location.search().q;
            $scope.activeQuery = $scope.formData.query;
            $scope.fetchRecords();
        } else {
            $scope.activeQuery = false;
        }
    });
});
